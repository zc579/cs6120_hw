#include "llvm/IR/PassManager.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/Module.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

namespace {

struct InsertLogOpPass : public PassInfoMixin<InsertLogOpPass> {
  PreservedAnalyses run(Module &M, ModuleAnalysisManager &) {
    LLVMContext &Ctx = M.getContext();

    // void logop(i32,i32,i32,i32)
    auto Func = M.getOrInsertFunction(
        "logop",
        FunctionType::get(Type::getVoidTy(Ctx),
                          {Type::getInt32Ty(Ctx),
                           Type::getInt32Ty(Ctx),
                           Type::getInt32Ty(Ctx),
                           Type::getInt32Ty(Ctx)},
                          false));

    bool Changed = false;

    for (auto &F : M) {
      if (F.isDeclaration()) continue;

      for (auto &B : F) {
        SmallVector<BinaryOperator*, 8> Ops;

        for (auto &I : B) {
          if (auto *BO = dyn_cast<BinaryOperator>(&I)) {
            unsigned op = BO->getOpcode();
            if (op == Instruction::Add ||
                op == Instruction::Sub ||
                op == Instruction::Mul ||
                op == Instruction::SDiv ||
                op == Instruction::UDiv) {

              if (BO->getType()->isIntegerTy(32))
                Ops.push_back(BO);
            }
          }
        }

        for (auto *BO : Ops) {
          IRBuilder<> Builder(BO->getNextNode());

          Value *L = BO->getOperand(0);
          Value *R = BO->getOperand(1);
          Value *Res = BO;

          int Code = -1;  

        auto Op = BO->getOpcode();

        if (Op == Instruction::Add) {
              Code = 0;
        } else if (Op == Instruction::Sub) {
              Code = 1;
        } else if (Op == Instruction::Mul) {
              Code = 2;
        } else if (Op == Instruction::SDiv || Op == Instruction::UDiv) {
              Code = 3;
        }
          Value *OpCodeVal = ConstantInt::get(Type::getInt32Ty(Ctx), Code);

          Builder.CreateCall(Func, {L, R, Res, OpCodeVal});
          Changed = true;
        }
      }
    }

    return Changed ? PreservedAnalyses::none() : PreservedAnalyses::all();
  }
};

} 

extern "C" LLVM_ATTRIBUTE_WEAK PassPluginLibraryInfo
llvmGetPassPluginInfo() {
  return {
    LLVM_PLUGIN_API_VERSION, "InsertLogOpPass", "v0.1",
    [](PassBuilder &PB) {
      PB.registerPipelineParsingCallback(
        [](StringRef Name, ModulePassManager &MPM,
           ArrayRef<PassBuilder::PipelineElement>) {
          if (Name == "insert-logop") {
            MPM.addPass(InsertLogOpPass());
            return true;
          }
          return false;
        });
    }
  };
}
