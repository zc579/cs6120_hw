; ModuleID = 'ive.ll'
source_filename = "test.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @foo(i32* noundef %0, i32 noundef %1) #0 {
  br label %3

3:                                                ; preds = %6, %2
  %.01 = phi i32 [ 0, %2 ], [ %10, %6 ]
  %.0 = phi i32 [ 0, %2 ], [ %ive.r3, %6 ]
  %ive.r1 = phi i32 [ 7, %2 ], [ %ive.inc2, %6 ]
  %ive.r3 = phi i32 [ 1, %2 ], [ %ive.inc4, %6 ]
  %4 = icmp slt i32 %.0, %1
  br i1 %4, label %5, label %11

5:                                                ; preds = %3
  br label %6

6:                                                ; preds = %5
  %7 = sext i32 %ive.r1 to i64
  %8 = getelementptr inbounds i32, i32* %0, i64 %7
  %9 = load i32, i32* %8, align 4
  %10 = add nsw i32 %.01, %9
  %ive.inc2 = add i32 %ive.r1, 3
  %ive.inc4 = add i32 %ive.r3, 1
  br label %3, !llvm.loop !6

11:                                               ; preds = %3
  ret i32 %.01
}

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @bar(i32* noundef %0, i32* noundef %1, i32 noundef %2) #0 {
  br label %4

4:                                                ; preds = %7, %3
  %.01 = phi i32 [ 0, %3 ], [ %15, %7 ]
  %.0 = phi i32 [ 0, %3 ], [ %ive.r3, %7 ]
  %ive.r1 = phi i32 [ -2, %3 ], [ %ive.inc2, %7 ]
  %ive.r3 = phi i32 [ 1, %3 ], [ %ive.inc4, %7 ]
  %5 = icmp slt i32 %.0, %2
  br i1 %5, label %6, label %16

6:                                                ; preds = %4
  br label %7

7:                                                ; preds = %6
  %8 = sext i32 %ive.r1 to i64
  %9 = getelementptr inbounds i32, i32* %0, i64 %8
  %10 = load i32, i32* %9, align 4
  %11 = sext i32 %ive.r1 to i64
  %12 = getelementptr inbounds i32, i32* %1, i64 %11
  %13 = load i32, i32* %12, align 4
  %14 = xor i32 %10, %13
  %15 = add nsw i32 %.01, %14
  %ive.inc2 = add i32 %ive.r1, 5
  %ive.inc4 = add i32 %ive.r3, 1
  br label %4, !llvm.loop !8

16:                                               ; preds = %4
  ret i32 %.01
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
