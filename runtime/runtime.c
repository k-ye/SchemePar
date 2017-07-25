#include <stdio.h>

typedef int long long Ptr;

Ptr read_int() {
    Ptr x = 0;
    // printf("Input integer: ");
    scanf("%lld", &x);
    return x;
}

void print_ptr(Ptr x) {
	printf("%lld", x);
	printf("\n");
}