extern "C" TargetExtra* __cdecl FUN_007235f0(SceneObject*);

namespace F3RangeKeys9154b0 {

struct FUN_00914ad0_9154b0 {float time,value1,value2;FUN_00914ad0_9154b0();};

struct NativeArray_9154b0:LargeArray_c9ac00 {void FUN_009147c0(unsigned int);};

struct NativeController_9154b0:TargetController {void FUN_00914c00();void FUN_00915470(FUN_00914ad0_9154b0*);};

struct NativeObject_9154b0:SceneObject {NativeController_9154b0* FUN_00825200(int*);};

extern TimeRange DAT_00f7aa78[];

extern TimeRange DAT_00f7a978[];

extern const float DAT_00db7260;

inline float RangeMinimum9154b0(const float& a,const float& b){return b<a?b:a;}

}

void FUN_00c9b250(SceneObject* object,float middle,bool alternate) {

 if(!object)return;

 TargetExtra* extra=FUN_007235f0(object);

 if(extra) {

  unsigned int flags=0;

  if(extra->link)flags=extra->link->GetFlags();

  unsigned int index=(flags>>8)&31;

  float first,last;

  if(alternate){first=F3RangeKeys9154b0::DAT_00f7aa78[index].start;last=F3RangeKeys9154b0::DAT_00f7aa78[index].end;}

  else {first=F3RangeKeys9154b0::DAT_00f7a978[index].start;last=F3RangeKeys9154b0::DAT_00f7a978[index].end;}

  float start=F3RangeKeys9154b0::RangeMinimum9154b0(first,extra->GetStart());

  float end=F3RangeKeys9154b0::RangeMinimum9154b0(last,extra->GetEnd());

  F3RangeKeys9154b0::NativeController_9154b0* controller=static_cast<F3RangeKeys9154b0::NativeObject_9154b0*>(object)->FUN_00825200(&reinterpret_cast<int&>(::DAT_010f32f8));

  if(controller && controller->mode<=1) {

   controller->FUN_00914c00();

   controller->mode=1;

   if(controller->keys.m_uiESize==0) {

    F3RangeKeys9154b0::FUN_00914ad0_9154b0 keys[3];

    keys[0].value1=start;

    keys[0].value2=end;

    keys[0].time=0.0f;

    keys[1].value1=first;

    keys[1].value2=last;

    keys[1].time=0.15f;

    keys[2].value2=keys[2].value1=1.0f;

    keys[2].time=0.5f;

    static_cast<F3RangeKeys9154b0::NativeArray_9154b0&>(controller->keys).FUN_009147c0(3);

    for(unsigned int i=0;i<3;++i)controller->FUN_00915470(&keys[i]);

    controller->start=0.0f;

    controller->end=1.0f;

    controller->frequency=1.0f;

    controller->phase=0.0f;

    controller->flags=(controller->flags&0xfff5)|0x1c5;

    controller->v35(F3RangeKeys9154b0::DAT_00db7260);

   }

  }

 }

 SceneNode* node=object->AsNode();

 if(node)for(unsigned int i=0;i<node->childCount;++i)FUN_00c9b250(node->children[i],middle,alternate);

}
