#include "h_a9296c396ec4.h"
int __fastcall SumVirtualResults(void* self) {
    int sum = 0;
    for (int i = 0; i < *(int*)((char*)self + 0x48); i++) {
        void* elem = ((void**)(*(void**)((char*)self + 0x44)))[i];
        void** vt = *(void***)elem;
        int (__thiscall *f)(void*) = (int (__thiscall *)(void*))vt[9];
        sum += f(elem);
    }
    return sum;
}
