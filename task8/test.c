#include <stddef.h>
int foo(int *A, int n) {
  int sum = 0;
  for (int i = 0; i < n; i++) {
    int idx = 3 * i + 7;   // 期望：乘法在循环外变成 r += 3 的递推
    sum += A[idx];
  }
  return sum;
}

int bar(int *A, int *B, int n) {
  int acc = 0;
  // 另一个用例：不同表达式但仍是 a*i + b
  for (int i = 0; i < n; i++) {
    int j = 5 * i - 2;
    acc += A[j] ^ B[j];
  }
  return acc;
}
