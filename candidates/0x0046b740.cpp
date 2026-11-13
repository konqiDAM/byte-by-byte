struct FNV_Cf5fe0_Node
{
    FNV_Cf5fe0_Node* next;
    FNV_Cf5fe0_Node* prev;
    void* data;
};
struct FNV_Cf5fe0_List
{
    FNV_Cf5fe0_Node* head;
    FNV_Cf5fe0_Node* tail;
    unsigned int count;
};
struct FNV_Cf5fe0_Global
{
    char pad[0x14];
    FNV_Cf5fe0_List list;
};
extern "C" FNV_Cf5fe0_Global* __cdecl FUN_0046b690();
extern "C" void* __fastcall FUN_00423640(void* context);

extern "C" void __cdecl FUN_00cf5fe0(void* p)
{
    if (!p)
        return;
    FNV_Cf5fe0_Global* g = FUN_0046b690();
    FNV_Cf5fe0_List* l = (FNV_Cf5fe0_List*)((char*)g + 0x14);
    FNV_Cf5fe0_Node* n = (FNV_Cf5fe0_Node*)FUN_00423640(&l->count);
    n->data = p;
    n->next = 0;
    n->prev = l->tail;
    if (l->tail)
        l->tail->next = n;
    else
        l->head = n;
    l->tail = n;
    ++l->count;
}
