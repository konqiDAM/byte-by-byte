#include "h_a9296c396ec4.h"

extern "C" void __cdecl FUN_009c9f80(FUN_00d408e0_1* a);

void __cdecl FUN_00d40910(BoxAgentRegistry* pkObj)
{
    FUN_00d408e0_1 kFuncs;
    kFuncs.b1 = 0;
    kFuncs.b2 = 0;
    FUN_009c9f80(&kFuncs);
    pkObj->FUN_00cfbbe0(kFuncs, 2, 2);
}
