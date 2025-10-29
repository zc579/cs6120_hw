; ModuleID = 'test.ll'
source_filename = "test.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @foo(i32* noundef %0, i32 noundef %1) #0 {
  br label %3

3:                                                ; preds = %12, %2
  %.01 = phi i32 [ 0, %2 ], [ %11, %12 ]
  %.0 = phi i32 [ 0, %2 ], [ %13, %12 ]
  %4 = icmp slt i32 %.0, %1
  br i1 %4, label %5, label %14

5:                                                ; preds = %3
  %6 = mul nsw i32 3, %.0
  %7 = add nsw i32 %6, 7
  %8 = sext i32 %7 to i64
  %9 = getelementptr inbounds i32, i32* %0, i64 %8
  %10 = load i32, i32* %9, align 4
  %11 = add nsw i32 %.01, %10
  br label %12

12:                                               ; preds = %5
  %13 = add nsw i32 %.0, 1
  br label %3, !llvm.loop !6

14:                                               ; preds = %3
  ret i32 %.01
}

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @bar(i32* noundef %0, i32* noundef %1, i32 noundef %2) #0 {
  br label %4

4:                                                ; preds = %17, %3
  %.01 = phi i32 [ 0, %3 ], [ %16, %17 ]
  %.0 = phi i32 [ 0, %3 ], [ %18, %17 ]
  %5 = icmp slt i32 %.0, %2
  br i1 %5, label %6, label %19

6:                                                ; preds = %4
  %7 = mul nsw i32 5, %.0
  %8 = sub nsw i32 %7, 2
  %9 = sext i32 %8 to i64
  %10 = getelementptr inbounds i32, i32* %0, i64 %9
  %11 = load i32, i32* %10, align 4
  %12 = sext i32 %8 to i64
  %13 = getelementptr inbounds i32, i32* %1, i64 %12
  %14 = load i32, i32* %13, align 4
  %15 = xor i32 %11, %14
  %16 = add nsw i32 %.01, %15
  br label %17

17:                                               ; preds = %6
  %18 = add nsw i32 %.0, 1
  br label %4, !llvm.loop !8

19:                                               ; preds = %4
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
