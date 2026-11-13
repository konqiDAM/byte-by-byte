
namespace f3m_007d5510 {

struct Actor;
struct xCtx;
struct xCombatMgr;

struct xStatic {
    float* Float();
};

struct xTimerC {
    float m_fStart;
    float m_fEnd;
    bool CheckTimer();
};

struct xOpts {
    unsigned char m_bFlag;
    char m_pad65[7];
    unsigned short m_uiAllow;
    bool Allows(unsigned short f) { return (m_uiAllow & f) != 0; }
};

struct Actor {
    int m_aiPad00[2];
    bool FUN_006f8d80();
    int FUN_006f58b0();
    int FUN_006f7370();
    const char* FUN_004e9a10();
    void FUN_006f8cb0(int flags);
};

struct xCtx {
    bool FUN_007995a0();
};

struct xCombatMgr {
    void FUN_0079d080(xCtx* ctx, int a, int b, int c);
};

struct xMelee {
    int m_i00;
    xCtx* m_pCtx;
    int m_aiPad04[2];
    int m_iState;
    int m_iStage;
    int m_i18;
    int m_aiPad1c[3];
    xTimerC m_kReaction;
    xTimerC m_kDuration;
    char m_apad38[0x2c];
    xOpts m_kOpts;

    void FUN_007d46e0();
    void FUN_007d4ba0();
    Actor* FUN_007ab510();
    Actor* FUN_007ab520();
    void FUN_007d2c70();
    void FUN_007d5470();
    void FUN_007d3c70();
    float FUN_007d2d10();
    float FUN_007d2b10();
    bool FUN_007d2b80(float a, float b, int c);
    void FUN_007d5510();
};

extern xStatic DAT_00f601dc;
extern xStatic DAT_00f5f324;
extern float DAT_0108cba0;
extern unsigned char DAT_0108c66c;
extern xCombatMgr* DAT_0108c7a8;

unsigned FUN_00456900();
void FUN_006195d0(const char* fmt, const char* name);

void xMelee::FUN_007d5510()
{
    if (m_iState != 2)
        return;
    if (DAT_0108cba0 - m_kReaction.m_fStart > m_kReaction.m_fEnd)
    {
        FUN_007d46e0();
        if (FUN_007ab510()->FUN_006f8d80())
            return;
        m_kOpts.m_bFlag = 1;
        return;
    }
    Actor* qfTOqo = FUN_007ab510();
    Actor* qpqRa = FUN_007ab520();
    int qSVM = qfTOqo->FUN_006f58b0();
    if ((qfTOqo->FUN_006f58b0() & 0xf) == 0)
    {
        FUN_007d46e0();
        return;
    }
    FUN_007d2c70();
    int qsSDDgz = qpqRa ? qpqRa->FUN_006f7370() : -1;
    if (qsSDDgz == 2 && m_iStage == 2)
    {
        m_i18 = 2;
        m_iStage = 3;
        FUN_007d5470();
    }
    if (m_kOpts.Allows((unsigned short)qSVM))
    {
        FUN_007d3c70();
        if (DAT_0108c66c)
            FUN_006195d0("%.20s has run out of room to dodge.", qfTOqo->FUN_004e9a10());
        FUN_007d46e0();
        return;
    }
    float qrEZrs = FUN_007d2d10();
    float qdqWL = FUN_007d2b10();
    if ((qSVM & 4) || (qSVM & 8))
    {
        if (qrEZrs > qdqWL)
        {
            if (FUN_007d2b80(qrEZrs, qdqWL, 0))
            {
                if (m_kDuration.CheckTimer())
                {
                    FUN_007d3c70();
                    FUN_007d4ba0();
                    return;
                }
            }
            else
                qfTOqo->FUN_006f8cb0(qSVM | 1);
        }
        else if (qrEZrs < *DAT_00f601dc.Float() && (qSVM & 1))
            qfTOqo->FUN_006f8cb0(qSVM & ~1);
    }
    else if (qSVM & 1)
    {
        if (qrEZrs <= *DAT_00f601dc.Float() && m_kDuration.CheckTimer())
        {
            FUN_007d3c70();
            FUN_007d46e0();
            return;
        }
    }
    if (qsSDDgz == 2)
    {
        float qxQHW = (float)(FUN_00456900() % 100);
        if ((qSVM & 0x100) && !m_pCtx->FUN_007995a0() && qxQHW > *DAT_00f5f324.Float())
            qfTOqo->FUN_006f8cb0((qSVM | 0x200) & ~0x100);
    }
    else if (qSVM & 0x200)
        qfTOqo->FUN_006f8cb0((qSVM | 0x100) & ~0x200);
    DAT_0108c7a8->FUN_0079d080(m_pCtx, 2, 0, 0);
}

}  // namespace f3m_007d5510
