#include "h_54f95791f678.h"
int __stdcall FUN_00cf6dc0(void* apUnused, void* a2, void* a3) {
    void* x = *(void**)a2;
    int idx = *(int*)((char*)x + 0x0C);
    void* y = *(void**)a3;
    unsigned int val = *(unsigned int*)((char*)y + 0x110 + idx * 4);
    return (int)((val >> 9) & 1);
}
