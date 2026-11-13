
#include <string.h>
#include <stdlib.h>

namespace f3m_007d1ae0 {

struct Actor;
struct Ref;
struct Process;
struct Tile;
struct Idle;
struct Sequence;
struct CombatController;

struct FileSub {
    virtual const char* v0();
    virtual const char* v1();
    virtual const char* v2();
    virtual const char* v3();
    virtual const char* v4();
    virtual const char* v5();
};

struct FileEntry {
    unsigned unk00, unk04, unk08, unk0c, unk10, unk14;
    FileSub sub;
};

struct Idle {
    unsigned unk000;
    unsigned unk004;
    unsigned unk008;
    unsigned unk00c;
    unsigned unk010;
    unsigned unk014;
    unsigned unk018;
    unsigned unk01c;
    unsigned unk020;
    unsigned unk024;
    unsigned unk028;
    unsigned unk02c;
    unsigned unk030;
    unsigned unk034;
    unsigned unk038;
    unsigned unk03c;
    unsigned unk040;
    unsigned unk044;
    unsigned unk048;
    unsigned unk04c;
    unsigned unk050;
    unsigned unk054;
    unsigned unk058;
    unsigned unk05c;
    unsigned unk060;
    unsigned unk064;
    unsigned unk068;
    unsigned unk06c;
    unsigned unk070;
    unsigned unk074;
    unsigned unk078;
    unsigned unk07c;
    unsigned unk080;
    unsigned unk084;
    unsigned unk088;
    unsigned unk08c;
    unsigned unk090;
    unsigned unk094;
    unsigned unk098;
    unsigned unk09c;
    unsigned unk0a0;
    unsigned unk0a4;
    unsigned unk0a8;
    unsigned unk0ac;
    unsigned unk0b0;
    unsigned unk0b4;
    unsigned unk0b8;
    unsigned unk0bc;
    unsigned unk0c0;
    unsigned unk0c4;
    unsigned unk0c8;
    unsigned unk0cc;
    float timer;
    bool FUN_0045e180();
    bool FUN_0045e1c0(int form);
    bool FUN_0045e240();
    FileEntry* FUN_00731a50();
    Sequence* FUN_00756610();
};

struct Sequence {
    float FUN_0049cac0(float v);
};

struct Process {
    unsigned unk00, unk04, unk08, unk0c, unk10, unk14, unk18, unk1c, unk20, unk24;
    int level;
    bool FUN_0072ff10(Actor* actor, unsigned refID, Ref* ref);
};

struct Tile {
    unsigned unk000;
    unsigned unk004;
    unsigned unk008;
    unsigned unk00c;
    unsigned unk010;
    unsigned unk014;
    unsigned unk018;
    unsigned unk01c;
    unsigned unk020;
    unsigned unk024;
    unsigned unk028;
    unsigned unk02c;
    unsigned unk030;
    unsigned unk034;
    unsigned unk038;
    unsigned unk03c;
    unsigned unk040;
    unsigned unk044;
    unsigned unk048;
    unsigned unk04c;
    unsigned unk050;
    unsigned unk054;
    unsigned unk058;
    unsigned unk05c;
    unsigned unk060;
    unsigned unk064;
    unsigned unk068;
    unsigned unk06c;
    unsigned unk070;
    unsigned unk074;
    unsigned unk078;
    unsigned unk07c;
    unsigned unk080;
    unsigned unk084;
    unsigned unk088;
    unsigned unk08c;
    unsigned unk090;
    unsigned unk094;
    unsigned unk098;
    unsigned unk09c;
    unsigned unk0a0;
    unsigned unk0a4;
    unsigned unk0a8;
    unsigned unk0ac;
    unsigned unk0b0;
    unsigned unk0b4;
    unsigned unk0b8;
    unsigned unk0bc;
    unsigned unk0c0;
    unsigned unk0c4;
    unsigned unk0c8;
    unsigned unk0cc;
    unsigned unk0d0;
    unsigned unk0d4;
    unsigned unk0d8;
    unsigned unk0dc;
    unsigned unk0e0;
    unsigned unk0e4;
    unsigned unk0e8;
    unsigned unk0ec;
    unsigned unk0f0;
    unsigned unk0f4;
    unsigned unk0f8;
    unsigned unk0fc;
    unsigned unk100;
    unsigned unk104;
    unsigned unk108;
    unsigned unk10c;
    unsigned unk110;
    unsigned unk114;
    unsigned unk118;
    unsigned unk11c;
    unsigned unk120;
    unsigned unk124;
    unsigned unk128;
    unsigned unk12c;
    unsigned unk130;
    unsigned unk134;
    unsigned unk138;
    unsigned unk13c;
    unsigned unk140;
    unsigned unk144;
    unsigned unk148;
    unsigned unk14c;
    unsigned unk150;
    unsigned unk154;
    unsigned unk158;
    unsigned unk15c;
    unsigned unk160;
    unsigned unk164;
    unsigned unk168;
    unsigned unk16c;
    unsigned unk170;
    unsigned unk174;
    unsigned unk178;
    unsigned unk17c;
    unsigned unk180;
    unsigned unk184;
    int* actions[5];
    void FUN_007acdf0(Ref* ref);
    void FUN_007aec10();
};

struct Ref {
    unsigned unk00, unk04, unk08, unk0c, unk10, unk14, unk18;
    unsigned refID;
    int FUN_004e8650(int v);
    void FUN_004ee000(Actor* actor, int a2, void* a3, int a4);
};

struct CombatController {
    unsigned unk000;
    unsigned unk004;
    unsigned unk008;
    unsigned unk00c;
    unsigned unk010;
    unsigned unk014;
    unsigned unk018;
    unsigned unk01c;
    unsigned unk020;
    unsigned unk024;
    unsigned unk028;
    unsigned unk02c;
    unsigned unk030;
    unsigned unk034;
    unsigned unk038;
    unsigned unk03c;
    unsigned unk040;
    unsigned unk044;
    unsigned unk048;
    unsigned unk04c;
    unsigned unk050;
    unsigned unk054;
    unsigned unk058;
    unsigned unk05c;
    unsigned unk060;
    unsigned unk064;
    unsigned unk068;
    unsigned unk06c;
    unsigned unk070;
    unsigned unk074;
    unsigned unk078;
    unsigned unk07c;
    unsigned unk080;
    unsigned unk084;
    unsigned unk088;
    unsigned unk08c;
    unsigned unk090;
    unsigned unk094;
    unsigned unk098;
    Tile* tile;
};

struct Actor {
    unsigned unk004;
    unsigned unk008;
    unsigned unk00c;
    unsigned unk010;
    unsigned unk014;
    unsigned unk018;
    unsigned unk01c;
    unsigned unk020;
    unsigned unk024;
    unsigned unk028;
    unsigned unk02c;
    unsigned unk030;
    unsigned unk034;
    unsigned unk038;
    unsigned unk03c;
    unsigned unk040;
    unsigned unk044;
    unsigned unk048;
    unsigned unk04c;
    unsigned unk050;
    unsigned unk054;
    unsigned unk058;
    unsigned unk05c;
    Process* process;
    unsigned unk064;
    unsigned unk068;
    unsigned unk06c;
    unsigned unk070;
    unsigned unk074;
    unsigned unk078;
    unsigned unk07c;
    unsigned unk080;
    unsigned unk084;
    unsigned unk088;
    unsigned unk08c;
    unsigned unk090;
    unsigned unk094;
    unsigned unk098;
    unsigned unk09c;
    unsigned unk0a0;
    unsigned unk0a4;
    unsigned unk0a8;
    unsigned unk0ac;
    unsigned unk0b0;
    unsigned unk0b4;
    unsigned unk0b8;
    unsigned unk0bc;
    unsigned unk0c0;
    unsigned unk0c4;
    unsigned unk0c8;
    unsigned unk0cc;
    unsigned unk0d0;
    unsigned unk0d4;
    unsigned unk0d8;
    unsigned unk0dc;
    unsigned unk0e0;
    unsigned unk0e4;
    unsigned unk0e8;
    unsigned unk0ec;
    unsigned unk0f0;
    unsigned unk0f4;
    unsigned char inCombat;
    virtual void v000();
    virtual void v004();
    virtual void v008();
    virtual void v00c();
    virtual void v010();
    virtual void v014();
    virtual void v018();
    virtual void v01c();
    virtual void v020();
    virtual void v024();
    virtual void v028();
    virtual void v02c();
    virtual void v030();
    virtual void v034();
    virtual void v038();
    virtual void v03c();
    virtual void v040();
    virtual void v044();
    virtual void v048();
    virtual void v04c();
    virtual void v050();
    virtual void v054();
    virtual void v058();
    virtual void v05c();
    virtual void v060();
    virtual void v064();
    virtual void v068();
    virtual void v06c();
    virtual void v070();
    virtual void v074();
    virtual void v078();
    virtual void v07c();
    virtual void v080();
    virtual void v084();
    virtual void v088();
    virtual void v08c();
    virtual void v090();
    virtual void v094();
    virtual void v098();
    virtual void v09c();
    virtual void v0a0();
    virtual void v0a4();
    virtual void v0a8();
    virtual void v0ac();
    virtual void v0b0();
    virtual void v0b4();
    virtual void v0b8();
    virtual void v0bc();
    virtual void v0c0();
    virtual void v0c4();
    virtual void v0c8();
    virtual void v0cc();
    virtual void v0d0();
    virtual void v0d4();
    virtual void v0d8();
    virtual void v0dc();
    virtual void v0e0();
    virtual void v0e4();
    virtual void v0e8();
    virtual void v0ec();
    virtual void v0f0();
    virtual void v0f4();
    virtual void v0f8();
    virtual void v0fc();
    virtual void v100();
    virtual void v104();
    virtual void v108();
    virtual void v10c();
    virtual void v110();
    virtual void v114();
    virtual void v118();
    virtual void v11c();
    virtual void v120();
    virtual void v124();
    virtual void v128();
    virtual void v12c();
    virtual void v130();
    virtual void v134();
    virtual void v138();
    virtual void v13c();
    virtual void v140();
    virtual void v144();
    virtual void v148();
    virtual void v14c();
    virtual void v150();
    virtual void v154();
    virtual void v158();
    virtual void v15c();
    virtual void v160();
    virtual void v164();
    virtual void v168();
    virtual void v16c();
    virtual void v170();
    virtual void v174();
    virtual void v178();
    virtual void v17c();
    virtual void v180();
    virtual void v184();
    virtual void v188();
    virtual void v18c();
    virtual void v190();
    virtual void v194();
    virtual void v198();
    virtual void v19c();
    virtual void v1a0();
    virtual void v1a4();
    virtual void v1a8();
    virtual void v1ac();
    virtual void v1b0();
    virtual void v1b4();
    virtual void v1b8();
    virtual void v1bc();
    virtual void v1c0();
    virtual void v1c4();
    virtual void v1c8();
    virtual void v1cc();
    virtual void v1d0();
    virtual void v1d4();
    virtual void v1d8();
    virtual void v1dc();
    virtual void v1e0();
    virtual Idle* GetAnimData();
};

struct CombatProc {
    unsigned unk00;
    CombatController* combatController;
    int state;
    const char* message;
    Ref* ref;
    unsigned baseObject;
    signed char status;
    Actor* FUN_007ab510();
    void FUN_007d1ae0();
};

__forceinline bool F4(Ref* r, unsigned id, Actor* a, Process* self) { return self->FUN_0072ff10(a, id, r); }

void CombatProc::FUN_007d1ae0()
{
    if (ref == 0)
    {
        message = "Targeted reference is NULL for some reason";
        state = 1;
        return;
    }
    Actor* actor = FUN_007ab510();
    Idle* idle = actor->GetAnimData();
    if (actor->process->level == 0 && idle)
    {
        if (status == 0)
        {
            if (!idle->FUN_0045e180())
                return;
            if (idle->FUN_0045e1c0(0))
                return;
            if (F4(ref, ref->refID, actor, actor->process))
            {
                status = 1;
                return;
            }
            status = -1;
        }
        else if (status == 1 || status == 3)
        {
            if (!idle->FUN_0045e180() || idle->FUN_0045e240())
            {
                if (status == 1)
                {
                    FileEntry* fe = idle->FUN_00731a50();
                    if (fe)
                    {
                        const char* str = fe->sub.v5();
                        if (str)
                        {
                            float val = 0.0f;
                            const char* b = strrchr(str, '_');
                            if (b)
                                val = (float)atof(b + 1);
                            Sequence* hy = idle->FUN_00756610();
                            if (hy)
                            {
                                float t = idle->timer;
                                if (hy->FUN_0049cac0(t) > val)
                                    status = 2;
                            }
                            else
                                status = 2;
                        }
                    }
                }
                if (status != 2)
                    return;
            }
        }
    }
    if (status != 3)
    {
        Tile* tile = combatController->tile;
        if (ref->refID != baseObject)
        {
            int arr[5];
            unsigned cnt = 0;
            memset(arr, 0, sizeof(arr));
            for (unsigned i = 0; i < 5; i++)
            {
                int* item = tile->actions[i];
                if (item && *item == (int)ref)
                {
                    arr[cnt] = item[1];
                    cnt++;
                }
            }
            tile->FUN_007acdf0(ref);
            for (unsigned j = 0; j < cnt; j++)
            {
                int c = ref->FUN_004e8650(arr[j]);
                if (c)
                {
                    if (c < 0)
                        c = -c;
                    ref->FUN_004ee000(actor, 1, (void*)arr[j], c);
                }
            }
        }
        else
        {
            tile->FUN_007acdf0(ref);
            ref->FUN_004ee000(actor, 1, 0, 1);
        }
        if (!actor->inCombat)
            return;
        tile->FUN_007aec10();
    }
    if (status == 2)
    {
        status = 3;
        return;
    }
    state = 2;
}

}  // namespace f3m_007d1ae0
