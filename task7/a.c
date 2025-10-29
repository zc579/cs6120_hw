// test.c
#include <stdio.h>

int main() {
    int a = 10;
    int b = 4;

    int s1 = a + b;  // add
    int s2 = a - b;  // sub
    int s3 = a * b;  // mul
    int s4 = a / b;  // div

    printf("%d %d %d %d\n", s1, s2, s3, s4);
    return 0;
}
