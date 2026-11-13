struct Heap01090a78 { void FUN_0086ba60(void* memory); };
extern Heap01090a78 DAT_01090a78;
struct Child615e50 { void FUN_00614f90(); };
struct Obj615e50 {
    char pad00[0x10];
    Child615e50* p10;
    char pad14[0xC];
    Obj615e50* arr[4];
    char pad30[0x2c];
    unsigned char flag5c;
    void FUN_00615e50();
};
void Obj615e50::FUN_00615e50()
{
    Child615e50* child = p10;
    if (child) {
        if (flag5c) {
            child->FUN_00614f90();
            DAT_01090a78.FUN_0086ba60(child);
            p10 = 0;
        }
    }
    Obj615e50** cursor = arr;
    int n = 4;
    do {
        if (*cursor) { (*cursor)->FUN_00615e50(); }
        ++cursor;
    } while (--n);
}
