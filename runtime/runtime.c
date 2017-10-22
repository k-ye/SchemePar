#include <stdint.h>
#include <stdio.h>

int64_t read_int() {
    int64_t x = 0;
    // printf("Input integer: ");
    scanf("%lld", &x);
    return x;
}

void print_ptr(int64_t x) {
	printf("%lld", x);
	printf("\n");
}