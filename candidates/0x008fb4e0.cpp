// 0x008fb4e0 - CreateResourceObject  (namespace fnv_00c89540, __cdecl, 4 int args)
// The shared symbols file has no entry for this function's mangled name, so the
// pack's symbol can only be produced by giving the source the same namespace and
// class names (that is what the mangling demands).
namespace fnv_00c89540 {

struct SpawnedBase_b7559
{
  public:
    virtual void unk00();
    int m_04;

    SpawnedBase_b7559();
    ~SpawnedBase_b7559();
};

struct FUN_00c894d0 : public SpawnedBase_b7559
{
  public:
    unsigned int unk08;
    unsigned int unk0c;
    unsigned int unk10;
    unsigned int unk14;
    unsigned int unk18;
    unsigned int unk1c;
    unsigned int unk20;
    unsigned int unk24;
    unsigned int unk28;

    static void* operator new(unsigned int count)
    {
        return FUN_0089eb90(count);
    }

    FUN_00c894d0(int a, int b, int c, int d, int e);
    virtual void unk00();
};

int __cdecl bhkUtilFunctions_FindNextCollisionObject(int object);

FUN_00c894d0* __cdecl CreateResourceObject(int first, int second, int resourceId, int finalArgument)
{
    FUN_00c894d0* result = 0;
    if (resourceId != 0)
    {
        int info = bhkUtilFunctions_FindNextCollisionObject(resourceId);
        if (info != 0)
            result = new FUN_00c894d0(first, second, resourceId, info, finalArgument);
    }
    return result;
}

}  // namespace fnv_00c89540
