; ModuleID = 'simp.ll'
source_filename = "test.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @foo(i32* noundef %0, i32 noundef %1) #0 {
  br label %3

3:                                                ; preds = %10, %2
  %.01 = phi i32 [ 0, %2 ], [ %9, %10 ]
  %.0 = phi i32 [ 0, %2 ], [ %ive.r3, %10 ]
  %ive.r = phi i32 [ 0, %2 ], [ %ive.inc, %10 ]
  %ive.r1 = phi i32 [ 7, %2 ], [ %ive.inc2, %10 ]
  %ive.r3 = phi i32 [ 1, %2 ], [ %ive.inc4, %10 ]
  %4 = icmp slt i32 %.0, %1
  br i1 %4, label %5, label %11

5:                                                ; preds = %3
  %6 = sext i32 %ive.r1 to i64
  %7 = getelementptr inbounds i32, i32* %0, i64 %6
  %8 = load i32, i32* %7, align 4
  %9 = add nsw i32 %.01, %8
  br label %10

10:                                               ; preds = %5
  %ive.inc = add i32 %ive.r, 3
  %ive.inc2 = add i32 %ive.r1, 3
  %ive.inc4 = add i32 %ive.r3, 1
  br label %3, !llvm.loop !6

11:                                               ; preds = %3
  %.01.lcssa = phi i32 [ %.01, %3 ]
  ret i32 %.01.lcssa
}

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @bar(i32* noundef %0, i32* noundef %1, i32 noundef %2) #0 {
  br label %4

4:                                                ; preds = %15, %3
  %.01 = phi i32 [ 0, %3 ], [ %14, %15 ]
  %.0 = phi i32 [ 0, %3 ], [ %ive.r3, %15 ]
  %ive.r = phi i32 [ 0, %3 ], [ %ive.inc, %15 ]
  %ive.r1 = phi i32 [ -2, %3 ], [ %ive.inc2, %15 ]
  %ive.r3 = phi i32 [ 1, %3 ], [ %ive.inc4, %15 ]
  %5 = icmp slt i32 %.0, %2
  br i1 %5, label %6, label %16

6:                                                ; preds = %4
  %7 = sext i32 %ive.r1 to i64
  %8 = getelementptr inbounds i32, i32* %0, i64 %7
  %9 = load i32, i32* %8, align 4
  %10 = sext i32 %ive.r1 to i64
  %11 = getelementptr inbounds i32, i32* %1, i64 %10
  %12 = load i32, i32* %11, align 4
  %13 = xor i32 %9, %12
  %14 = add nsw i32 %.01, %13
  br label %15

15:                                               ; preds = %6
  %ive.inc = add i32 %ive.r, 5
  %ive.inc2 = add i32 %ive.r1, 5
  %ive.inc4 = add i32 %ive.r3, 1
  br label %4, !llvm.loop !8

16:                                               ; preds = %4
  %.01.lcssa = phi i32 [ %.01, %4 ]
  ret i32 %.01.lcssa
}

attributes #0 = { noinline nounwind uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 7, !"PIC Level", i32 2}
!2 = !{i32 7, !"PIE Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 1}
!4 = !{i32 7, !"frame-pointer", i32 2}
!5 = !{!"Ubuntu clang version 14.0.0-1ubuntu1.1"}
!6 = distinct !{!6, !7}
!7 = !{!"llvm.loop.mustprogress"}
!8 = distinct !{!8, !7}
