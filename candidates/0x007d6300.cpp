extern float DAT_01012054;
extern const float DAT_010162c0;
extern float DAT_00f601ec;
extern float DAT_0108cba0;
extern char str_00e1d4f8[];
extern double DAT_00e1a690;
namespace q7d6300 {
struct Actor;
struct Ctx
{
    bool FUN_006f8d60();
    bool FUN_006f8c60();
    float FUN_004e6d80();
};
struct Res
{
    int m_0;
    Res() {}
};
struct Pt { float x, y, z, w; };
struct Actor
{
    Pt* FUN_004eea80(Pt* out);
};
struct Proc9c
{
    int unk00;
    unsigned int m_flags;
    void FUN_007ae580(Pt* p);
};
struct Owner
{
    char pad[0x9c];
    Proc9c* m_9c;
    char padA0[0xf0 - 0xa0];
    void* m_f0;
};
struct Sub64
{
    void FUN_007d41b0(Owner* o);
};
float __cdecl FUN_007b8c50(Ctx* c, Actor* a, int b);
float __cdecl FUN_007b7810(Ctx* c, void* p);
Res __cdecl FUN_007b8030(Actor* a, int b);
struct Task
{
    int unk00;
    Owner* m_owner;
    int m_8;
    const char* m_c;
    int m_state;
    int m_14;
    char pad18[0x48 - 0x18];
    float m_start;
    float m_wait;
    char pad50[0x58 - 0x50];
    float m_58;
    float m_5c;
    int unk60;
    Sub64 m_64;
    Ctx* FUN_007ab510();
    Actor* FUN_007ab520();
    void FUN_007d5470();
    void FUN_007d61b0();
    void FUN_007d5780();
    void FUN_007d5510();
    void FUN_007d5b00();
    void FUN_007d5e20();
    void FUN_007ab580();
    void FUN_007ab550(const Res& r, int a);
    float GetRange()
    {
        if (m_5c < 0.0f)
            m_5c = FUN_007b8c50(FUN_007ab510(), FUN_007ab520(), 0);
        return m_5c;
    }
    float GetDist()
    {
        Ctx* c = FUN_007ab510();
        if (m_58 < 0.0f)
        {
            void* f = m_owner->m_f0;
            m_58 = FUN_007b7810(c, f);
        }
        return m_58;
    }
    void FUN_007d6300();
};
void Task::FUN_007d6300()
{
    Ctx* ctx = FUN_007ab510();
    Actor* actor = FUN_007ab520();
    m_5c = DAT_01012054;
    m_64.FUN_007d41b0(m_owner);
    FUN_007d5470();
    if (m_state == 3 || m_state == 4)
    {
        if (ctx->FUN_006f8d60() && !ctx->FUN_006f8c60())
        {
            if (m_wait == 0.0f)
            {
                m_start = DAT_0108cba0;
                m_wait = DAT_010162c0;
            }
            else if (DAT_0108cba0 - m_start > m_wait)
            {
                m_owner->m_9c->m_flags |= 2;
                Proc9c* p = m_owner->m_9c;
                Pt tmp;
                p->FUN_007ae580(actor->FUN_004eea80(&tmp));
                m_c = str_00e1d4f8;
                m_8 = 1;
            }
        }
        else if (ctx->FUN_006f8c60())
            m_wait = 0.0f;
    }
    else
        m_wait = 0.0f;
    switch (m_state)
    {
    case 0: FUN_007d61b0(); break;
    case 2: FUN_007d5510(); break;
    case 1: FUN_007d5780(); break;
    case 3: FUN_007d5b00(); break;
    case 4: FUN_007d5e20(); break;
    }
    bool done = false;
    if (m_14 == 3 && m_state != 3)
        done = !(GetRange() - GetDist() < ctx->FUN_004e6d80() * DAT_00f601ec * DAT_00e1a690);
    if (!done)
    {
        Res r = FUN_007b8030(actor, 2);
        FUN_007ab550(r, 4);
    }
    else
        FUN_007ab580();
}
}
