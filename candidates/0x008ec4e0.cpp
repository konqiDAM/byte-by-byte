// bhkRagdollController-style destructor: 3 polymorphic bases at 0, 0x260, 0x290,
// then refcounted pointers, a 0x94 chunk, an array and an out-of-line member dtor.

#include <intrin.h>

extern "C" __declspec(dllimport) void* __stdcall TlsGetValue(unsigned long idx);

struct f3_VObj {
    virtual void v00(); virtual void v04(); virtual void v08(); virtual void v0c();
    virtual void v10(); virtual void v14(); virtual void v18(); virtual void v1c();
    virtual void v20(); virtual void v24(); virtual void v28(); virtual void v2c();
    virtual void v30(); virtual void v34(); virtual void v38(); virtual void v3c();
    virtual void v40(); virtual void v44(); virtual void v48(); virtual void v4c();
    virtual void v50(); virtual void v54(); virtual void v58(); virtual void v5c();
    virtual void v60(); virtual void v64(); virtual void v68(); virtual void v6c();
    virtual void v70(); virtual void v74(); virtual void v78(); virtual void v7c();
    virtual void v80(); virtual void v84(); virtual void v88(); virtual void v8c();
    virtual void v90(); virtual void v94(); virtual void v98();
};

struct f3_Ref {
    virtual void r0();
    virtual void r1();
    int m_refCount;
};

struct f3_RefPtr {
    f3_Ref* m_p;
    ~f3_RefPtr() {
        f3_Ref* p = m_p;
        if (p && InterlockedDecrement((volatile long*)&p->m_refCount) == 0)
            p->r1();
    }
};

struct f3_Sub3 {
    virtual ~f3_Sub3() {}
    virtual void s3();
    int a[100];
};

struct f3_Sub2 {
    virtual ~f3_Sub2();
    virtual void s2();
    int a[11];
};

struct f3_Level {
    void* m00;
    void* m04;
    void* m08;
    void* getter();
    void unlock(void* sub);
};

struct f3_Sub1 {
    virtual ~f3_Sub1();
    virtual void s1();
    int m4;
    f3_Level* m8;
    int a[149];
};

struct f3_Heap { void deallocate(void* block, int bytes, unsigned tag); };
extern unsigned f3_tlsIndex;

extern void f3_release_fn();
extern void __stdcall f3_dealloc_chunk(void* p, unsigned size, unsigned align, void* fn);

struct f3_Chunk {
    int a[37];
    ~f3_Chunk() { f3_dealloc_chunk(this, 4, 2, (void*)&f3_release_fn); }
};

struct f3_Arr {
    void* m_data;
    int m_size;
    int m_capFlags;
    ~f3_Arr() {
        int c = m_capFlags;
        if (!(c & 0x80000000)) {
            int cap = c & 0x3fffffff;
            f3_Heap* heap = (f3_Heap*)TlsGetValue(f3_tlsIndex);
            heap->deallocate(m_data, cap * 64, 0x17);
        }
    }
};

struct f3_Obj4d8 {
    int a[4];
    ~f3_Obj4d8();
};

struct f3_C : f3_Sub1, f3_Sub2, f3_Sub3 {
    f3_RefPtr m424;
    f3_RefPtr m428;
    f3_RefPtr m42c;
    int m430;
    int m434;
    f3_Chunk m438;
    f3_Arr m4cc;
    f3_Obj4d8 m4d8;
    virtual ~f3_C();
};

f3_C::~f3_C() {
    m4cc.m_size = 0;
    f3_Level* p = m8 ? (f3_Level*)m8->getter() : 0;
    void* q = p->m08;
    f3_VObj* t = q ? *(f3_VObj**)((char*)q + 0x310) : 0;
    _ReadWriteBarrier();
    if (t) {
        t->v98();
        if (m8)
            m8->unlock((void*)(f3_Sub3*)this);
        t->v98();
    }
}
