#include <string>

void __cdecl FUN_00bff0b2();
void __cdecl FUN_00bff073();
void __cdecl FUN_00c01c9b(char* _First1, unsigned int _Size, const char* _First2, unsigned int _Count);
void __cdecl FUN_00c01c20(char* _First1, unsigned int _Size, const char* _First2, unsigned int _Count);
void __cdecl FUN_004274f0(char* _First1, unsigned int _Size, const char* _First2, unsigned int _Count);

struct Str_00668760 : std::string {
    Str_00668760& FUN_00668760(const size_type _Off, size_type _N0,
        const Str_00668760& _Right, const size_type _Roff, size_type _Count);
};

Str_00668760& Str_00668760::FUN_00668760(const size_type _Off, size_type _N0,
    const Str_00668760& _Right, const size_type _Roff, size_type _Count)
{
    if (_Mysize < _Off || _Right.size() < _Roff)
        FUN_00bff0b2();
    if (_Mysize - _Off < _N0)
        _N0 = _Mysize - _Off;
    size_type _Num = _Right.size() - _Roff;
    if (_Num < _Count)
        _Count = _Num;
    if (npos - _Count <= _Mysize - _N0)
        FUN_00bff073();

    size_type _Nm = _Mysize - _N0 - _Off;
    size_type _Newsize = _Mysize + _Count - _N0;
    if (_Mysize < _Newsize)
        _Grow(_Newsize);

    if (this != &_Right) {
        FUN_00c01c9b(_Myptr() + _Off + _Count, _Myres - _Off - _Count,
            _Myptr() + _Off + _N0, _Nm);
        FUN_00c01c20(_Myptr() + _Off, _Myres - _Off,
            _Right._Myptr() + _Roff, _Count);
    } else if (_Count <= _N0) {
        FUN_00c01c9b(_Myptr() + _Off, _Myres - _Off,
            _Myptr() + _Roff, _Count);
        FUN_00c01c9b(_Myptr() + _Off + _Count, _Myres - _Off - _Count,
            _Myptr() + _Off + _N0, _Nm);
    } else if (_Roff <= _Off) {
        FUN_00c01c9b(_Myptr() + _Off + _Count, _Myres - _Off - _Count,
            _Myptr() + _Off + _N0, _Nm);
        FUN_00c01c9b(_Myptr() + _Off, _Myres - _Off,
            _Myptr() + _Roff, _Count);
    } else if (_Off + _N0 <= _Roff) {
        FUN_004274f0(_Myptr() + _Off + _Count, _Myres - _Off - _Count,
            _Myptr() + _Off + _N0, _Nm);
        FUN_004274f0(_Myptr() + _Off, _Myres - _Off,
            _Myptr() + (_Roff + _Count - _N0), _Count);
    } else {
        FUN_004274f0(_Myptr() + _Off, _Myres - _Off,
            _Myptr() + _Roff, _N0);
        FUN_004274f0(_Myptr() + _Off + _Count, _Myres - _Off - _Count,
            _Myptr() + _Off + _N0, _Nm);
        FUN_004274f0(_Myptr() + _Off + _N0, _Myres - _Off - _N0,
            _Myptr() + _Roff + _Count, _Count - _N0);
    }
    _Eos(_Newsize);
    return *this;
}
