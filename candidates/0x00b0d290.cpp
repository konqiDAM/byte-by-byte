// MTRenderingSystem_TaskThreadCallback (0x00b0d290): the per-stage scene accumulation loop.
// Structure ported from the FNV twin at 0x00ba3190 (same routine; both builds /O2).
#include <intrin.h>

namespace fnv_00ba3190 {

struct RefObj {
    virtual void v00();
    virtual void DeleteThis();
    unsigned int m_uiRefCount;
};

struct CullBase {
    const void* vtable;
    int unk04, unk08, unk0c, unk10, unk14, unk18, unk1c;
    int unk20, unk24, unk28, unk2c, unk30, unk34, unk38, unk3c;
    int unk40, unk44, unk48, unk4c, unk50, unk54, unk58, unk5c;
    int unk60, unk64, unk68, unk6c, unk70, unk74, unk78, unk7c;
    int unk80, unk84, unk88, unk8c;
    CullBase(void* visibleSet);
};

extern const void* f3_cullVtable;

struct Culler : CullBase {
    unsigned int cullMode;
    int unk94, unk98, unk9c, unka0, unka4, unka8, unkac;
    int unkb0, unkb4, unkb8;
    void* field_bc;
    void* field_c0;
    void* field_c4;

    Culler(void* visibleSet = 0) : CullBase(visibleSet) {
        vtable = &f3_cullVtable;
        cullMode = 0;
        field_bc = 0;
        field_c0 = 0;
        field_c4 = 0;
    }
    void FUN_004a0f60();
    __forceinline ~Culler() { FUN_004a0f60(); }
};

struct TaskRecord {
    void* unk00;
    void* unk04;
    void* unk08;
    void* unk0C;
    void* unk10;
    void* unk14;
    int unk18;
    int unk1C;
};

extern TaskRecord f3_taskRecords[23];
extern unsigned int f3_fsSlot;

struct StageWait {
    void Wait(int threadIndex, int stage);
};
extern StageWait f3_stageWait;

struct SceneSub {
    void FUN_00c47770();
};

extern bool f3_syncOn;
extern void* f3_semaphore;
extern volatile long f3_semCount;

void __cdecl f3_accumulate(void* a, void* b, Culler* c);
void __cdecl f3_accumulateList(void* a, void* b, Culler* c);
static void AddB(void* a, void* b, Culler* c) { f3_accumulate(a, b, c); }
static void AddC(void* a, void* b, Culler* c) { f3_accumulateList(a, b, c); }

static void ReleaseRef(RefObj*& rp) {
    RefObj* p = rp;
    if (p) {
        if (InterlockedDecrement((volatile long*)&p->m_uiRefCount) == 0)
            p->DeleteThis();
        rp = 0;
    }
}

void FUN_00ba3190() {
    for (int i = 1; i < 24; ++i) {
        TaskRecord* rec = &f3_taskRecords[i - 1];
        f3_stageWait.Wait(0, i);
        if (rec->unk14) {
            *(int*)((char*)(((char**)__readfsdword(0x2c))[f3_fsSlot]) + 0x2a4) = rec->unk1C;
            Culler cull;
            RefObj* p = (RefObj*)rec->unk14;
            if (p) {
                cull.field_c4 = p;
                InterlockedIncrement((volatile long*)&p->m_uiRefCount);
            }
            cull.cullMode = (unsigned int)rec->unk18;
            cull.field_c0 = rec->unk04;
            if (rec->unk08)
                AddB(rec->unk00, rec->unk08, &cull);
            if (rec->unk0C)
                AddC(rec->unk00, rec->unk0C, &cull);
            if (rec->unk10)
                AddC(rec->unk00, rec->unk10, &cull);
            rec->unk1C = 0;
            rec->unk0C = 0;
            rec->unk10 = 0;
            ReleaseRef((RefObj*&)rec->unk14);
            ReleaseRef((RefObj*&)rec->unk00);
            ReleaseRef((RefObj*&)rec->unk08);
            SceneSub* s = (SceneSub*)rec->unk04;
            if (s) {
                s->FUN_00c47770();
                g_memoryManager.Free(s);
                rec->unk04 = 0;
            }
        }
        if (f3_syncOn) {
            ReleaseSemaphore(f3_semaphore, 1, 0);
            InterlockedIncrement(&f3_semCount);
        }
    }
}

}  // namespace fnv_00ba3190
