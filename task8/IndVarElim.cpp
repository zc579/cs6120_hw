#include "llvm/ADT/SmallVector.h"
#include "llvm/ADT/Optional.h"
#include "llvm/ADT/APInt.h"
#include "llvm/ADT/MapVector.h"
#include "llvm/Analysis/LoopInfo.h"
#include "llvm/Analysis/ScalarEvolution.h"
#include "llvm/Analysis/ScalarEvolutionExpressions.h"
#include "llvm/Transforms/Utils/ScalarEvolutionExpander.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/PassManager.h"
#include "llvm/IR/PatternMatch.h"
#include "llvm/IR/Value.h"
#include "llvm/IR/Verifier.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h"
#include <map>

using namespace llvm;
namespace {
struct IndVarElimPass : public PassInfoMixin<IndVarElimPass> {
  static const SCEVAddRecExpr *getCanonicalIV(PHINode *Phi,
                                              Loop *L,
                                              ScalarEvolution &SE) {
    if (!L->contains(Phi->getParent()))
      return nullptr;
    auto *AR = dyn_cast<SCEVAddRecExpr>(SE.getSCEV(Phi));
    if (!AR || AR->getLoop() != L)
      return nullptr;
    const SCEV *Step = AR->getStepRecurrence(SE);
    if (!isa<SCEVConstant>(Step))
      return nullptr;
    return AR;
  }

  static Optional<std::pair<const SCEV*, const SCEV*>>
  matchAffineUsingIV(const SCEV *Expr,
                     const SCEVAddRecExpr *IV,
                     ScalarEvolution &SE) {
    auto *AR = dyn_cast<SCEVAddRecExpr>(Expr);
    if (!AR || AR->getLoop() != IV->getLoop())
      return None;

    // AR == {Base, +K}，IV == {Start, +C}
    const SCEV *K  = AR->getStepRecurrence(SE);
    const SCEV *C  = IV->getStepRecurrence(SE);

    auto *KC = dyn_cast<SCEVConstant>(K);
    auto *CC = dyn_cast<SCEVConstant>(C);
    if (!KC || !CC) return None;

    const APInt &KVal = KC->getAPInt();
    const APInt &CVal = CC->getAPInt();
    if (CVal.isZero()) return None;

    if (KVal.srem(CVal) != 0)
      return None;

    APInt AVal = KVal.sdiv(CVal);

    const SCEV *A = SE.getConstant(AVal);

    // A*i + B == AR => B = Base - A*Start
    const SCEV *Base   = AR->getStart();
    const SCEV *AStart = SE.getMulExpr(A, IV->getStart());
    const SCEV *B      = SE.getMinusSCEV(Base, AStart);
    return std::make_pair(A, B);
  }

  static Value* expandAt(const SCEV *S, Type *Ty, Instruction *InsertBefore,
                         ScalarEvolution &SE) {
    const DataLayout &DL = InsertBefore->getModule()->getDataLayout();
    SCEVExpander Exp(SE, DL, "ive", /*PreserveLCSSA=*/false);
    return Exp.expandCodeFor(S, Ty, InsertBefore);
  }

  PreservedAnalyses run(Loop &L, LoopAnalysisManager &LAM,
                        LoopStandardAnalysisResults &AR, LPMUpdater &U) {

    ScalarEvolution &SE = AR.SE;
    DominatorTree   &DT = AR.DT;
    (void)DT; 
    // LoopInfo &LI = AR.LI;

    BasicBlock *Header    = L.getHeader();
    BasicBlock *Preheader = L.getLoopPreheader();
    BasicBlock *Latch     = L.getLoopLatch();
    if (!Header || !Preheader || !Latch)
      return PreservedAnalyses::all();
      
    PHINode *IndPhi = nullptr;
    const SCEVAddRecExpr *IV = nullptr;
    for (PHINode &P : Header->phis()) {
      if (auto *ARiv = getCanonicalIV(&P, &L, SE)) {
        IndPhi = &P;
        IV = ARiv;
        break;
      }
    }
    if (!IV)
      return PreservedAnalyses::all();

    bool Changed = false;

    SmallVector<Instruction*, 16> Targets;
    SmallVector<std::pair<const SCEV*, const SCEV*>, 16> Plans;

    for (auto *BB : L.blocks()) {
      for (Instruction &I : *BB) {
        if (&I == IndPhi) continue;
        if (I.mayReadOrWriteMemory()) continue; 
        if (!I.getType()->isIntegerTy()) continue;

        const SCEV *S = SE.getSCEV(&I);
        if (auto AB = matchAffineUsingIV(S, IV, SE)) {
          Targets.push_back(&I);
          Plans.push_back(*AB);
        }
      }
    }

    if (Targets.empty())
      return PreservedAnalyses::all();

    std::map<std::pair<const SCEV*, const SCEV*>, PHINode*> Built;

    IRBuilder<> HB(&*Header->getFirstInsertionPt());
    IRBuilder<> LB(Latch->getTerminator());
    Instruction *PHInsert = Preheader->getTerminator(); 

    SmallVector<Instruction*, 16> ToErase;

    for (size_t i = 0; i < Targets.size(); ++i) {
      Instruction *I = Targets[i];
      auto [A, B] = Plans[i];

      Type *ITy = I->getType();
      auto Key = std::make_pair(A, B);
      PHINode *R = nullptr;

      auto It = Built.find(Key);
      if (It == Built.end()) {
        // base = a*Start + b  （preheader）
        const SCEV *AStart = SE.getMulExpr(A, IV->getStart());
        const SCEV *BaseS  = SE.getAddExpr(AStart, B);
        Value *BaseV = expandAt(BaseS, ITy, PHInsert, SE);

        // step = a*C 
        const SCEV *StepS = SE.getMulExpr(A, IV->getStepRecurrence(SE));
        Value *StepV = expandAt(StepS, ITy, PHInsert, SE);

        // r = phi [base,preheader], [r.next,latch]
        R = HB.CreatePHI(ITy, 2, "ive.r");
        Value *RNext = LB.CreateAdd(R, StepV, "ive.inc");

        R->addIncoming(BaseV, Preheader);
        R->addIncoming(RNext, Latch);

        Built.emplace(Key, R);
      } else {
        R = It->second;
      }

      I->replaceAllUsesWith(R);
      ToErase.push_back(I);
      Changed = true;
    }

    for (Instruction *Dead : ToErase)
      Dead->eraseFromParent();

    return Changed ? PreservedAnalyses::none() : PreservedAnalyses::all();
  }
};

} // end anonymous namespace

llvm::PassPluginLibraryInfo getIndVarElimPassPluginInfo() {
  return {LLVM_PLUGIN_API_VERSION, "IndVarElimPass", LLVM_VERSION_STRING,
          [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, LoopPassManager &LPM,
                   ArrayRef<PassBuilder::PipelineElement>) {
                  if (Name == "indvar-elim") {
                    LPM.addPass(IndVarElimPass());
                    return true;
                  }
                  return false;
                });
          }};
}

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
  return getIndVarElimPassPluginInfo();
}
