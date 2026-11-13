class CF4BC0Object
{
  public:
    virtual void Unk_00();
    virtual void Unk_01();
    virtual void Unk_02();
    virtual void Unk_03();
    virtual unsigned int GetSaveType();
};

void __cdecl FUN_00cf4bc0(CF4BC0Stream& kStream, CF4BC0Object* pkObject)
{
    unsigned int uiType = pkObject->GetSaveType();
    CF4BC0Saver* pkSaver = CF4BC0CreateSaver(uiType);
    pkSaver->SetObject(pkObject);
    CF4BC0SaveBinary(kStream, uiType);
    pkSaver->SaveBinary(kStream);
    pkSaver->DeleteThis(true);
}
