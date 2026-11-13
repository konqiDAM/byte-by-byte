#include <math.h>
#include <stdlib.h>

// ---- candidate ----
namespace c11 {
struct CList
{
    void* item;
    CList* next;
};

struct CItem
{
    int unk00;
    int unk04;
    void* unk08;
    float FUN_0047d120();
};

struct CMenu
{
    char pad000[0x74];
    int unk74;
    char pad078[0x80 - 0x78];
    float unk80;
    float unk84;
    char pad088[0xc4 - 0x88];
    char unkC4[4];
};

struct CTile
{
    bool FUN_00becf80(int);
};

extern CMenu* DAT_01075e6c;
extern int DAT_01075e7c;
extern void* DAT_0107a104;
float __cdecl FUN_0047ca30(float, float);
void __cdecl FUN_00543420(int, void*, void*, float*);

inline bool ListContains(CMenu* menu, void* key)
{
    CList* p = (CList*)((char*)menu + 0xc4);
    if (p)
    {
        CList* q = (CList*)((char*)p + 4);
        if (q)
        {
            for (; q; q = q->next)
            {
                if (!q->item)
                    break;
                if (*(void**)q->item == key)
                    return true;
            }
        }
    }
    return false;
}

float FUN_00632910(CTile* tile, CItem* item)
{
    float amount = item->FUN_0047d120();
    float base = amount;
    float result;
    bool b5 = ListContains(DAT_01075e6c, tile);
    bool b8 = tile->FUN_00becf80(DAT_01075e7c);
    if (amount < 0.0f)
        result = -1.0f;
    else if ((b5 && !b8) || (!b5 && b8))
    {
        amount *= DAT_01075e6c->unk80;
        if (DAT_01075e6c->unk74 > 0)
            amount = (1.0 - abs(DAT_01075e6c->unk74) / 100.0) * amount;
        else if (DAT_01075e6c->unk74 < 0)
            amount = (abs(DAT_01075e6c->unk74) / 100.0 + 1.0) * amount;
        FUN_00543420(0x11, DAT_0107a104, item->unk08, &amount);
        if (fabs(amount) > 1.0f)
            amount = FUN_0047ca30(amount, 1.0f);
        else
            amount = FUN_0047ca30(amount, 0.1f);
        result = amount > base ? amount : base;
    }
    else
    {
        amount *= DAT_01075e6c->unk84;
        if (DAT_01075e6c->unk74 > 0)
            amount = (abs(DAT_01075e6c->unk74) / 100.0 + 1.0) * amount;
        else if (DAT_01075e6c->unk74 < 0)
            amount = (1.0 - abs(DAT_01075e6c->unk74) / 100.0) * amount;
        if (fabs(amount) > 1.0f)
            amount = FUN_0047ca30(amount, 1.0f);
        else
            amount = FUN_0047ca30(amount, 0.1f);
        result = amount < base ? amount : base;
    }
    return result;
}

} // namespace c11
