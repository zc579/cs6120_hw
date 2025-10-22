#include <stdio.h>

void logop(int lhs, int rhs, int result, int op) {
    const char *OPS[4] = {"+", "-", "*", "/"};
    printf("logop: %d %s %d = %d\n", lhs, OPS[op], rhs, result);
}
