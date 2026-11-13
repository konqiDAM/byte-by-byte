namespace f3m_00bcd160 {
namespace f3m_00bcd160 {

struct Win32FileWrite
{
    int unk00;
    int m_openMode;
    int m_createMode;
    unsigned char m_noBuffering;
    unsigned char unk0d;
    unsigned char unk0e;
    unsigned char unk0f;
    HANDLE m_handle;

    int FUN_00bcd010(void* buf, DWORD len, int unused, unsigned __int64* outRead);
};

int Win32FileWrite::FUN_00bcd010(void* buf, DWORD len, int unused, unsigned __int64* outRead)
{
    DWORD nRead = 0;
    int rc;
    if (m_noBuffering)
        rc = 4;
    else if ((unsigned int)WriteFile(m_handle, buf, len, &nRead, 0) <= 0)
        rc = FUN_00bccf50(GetLastError());
    else
    {
        rc = 0;
        *outRead = nRead;
    }
    return rc;
}
}  // namespace f3m_00bcd160
}  // namespace f3m_00bcd160
