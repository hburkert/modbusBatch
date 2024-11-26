"""
modbusBatch helpers

    word_swap   : swap two registers (r1,r2) -> (r2,1)
    qword_swap  : swap four registers (r1,r2,r3,r4) -> (r4,r3,r2,r1)

    u16         : decode BE encoded register (network order) to unsigned
    s16         : decode BE encoded register (network order) to unsigned
    u32be       : decode BE encoded register pair (network order) to unsigned
    u32le       : decode LE encoded register pair (word swapped) to unsigned
    s32be       : decode BE encoded register pair (network order) to signed
    s32le       : decode LE encoded register pair (word swapped) to signed
    u64be       : decode BE encoded quadruple register (network order) to unsigned
    s64be       : decode BE encoded quadruple register (network order) to signed
    Unpack functions receive a byte buffer representing one or more 
    registers (16 bit unsigned integer in network order) 
    and an optional scaling factor and an optional rounding value.
    Depending on factor and rounding the result will be integer or float.

    regs_to_str : byte buffer to null-terminated utf8-string
"""
from __future__ import annotations
from struct import unpack_from


def word_swap(buf: bytes) -> bytes:
    return buf[2:4] + buf[0:2]


def qword_swap(buf: bytes) -> bytes:
    return buf[6:8] + buf[4:6] + buf[2:4] + buf[0:2]


def u16(buf: bytes, f: int | float = 1, r: int = 0) -> int | float:
    """  unsigned int BE to unsigned """
    return round(unpack_from( ">H", buf)[0] * f, r)


def s16(buf: bytes, f: int | float = 1, r: int = 0) -> int | float:
    """  signed int BE to unsigned """
    return round(unpack_from( ">h", buf )[0] * f, r)


def u32be(buf: bytes, f: int | float = 1, r: int = 0) -> int | float:
    """  double word from raw buffer (high order word first) to unsigned """
    return round(unpack_from('>L', buf)[0] * f, r)


def u32le(buf: bytes, f: int | float = 1, r: int = 0) -> int | float:
    """  double word from raw buffer (low order word first) to unsigned """
    return round(unpack_from('>L', word_swap( buf ) )[0] * f, r)


def s32be(buf: bytes, f: int | float = 1, r: int = 0) -> int | float:
    """  double word from raw buffer (high order word first) to signed """
    return round(unpack_from('>l', buf)[0] * f, r)


def s32le(buf: bytes, f: int | float = 1, r: int = 0) -> int | float:
    """  double word from raw buffer (low order word first) to signed """
    return round(unpack_from('>l', word_swap( buf ) )[0] * f, r)


def u64be(buf: bytes, f: int | float = 1, r: int = 0) -> int | float:
    """  quadruple word from raw buffer (high to low from left to right) to unsigned """
    return round(unpack_from('>Q', buf)[0] * f, r)


def u64le(buf: bytes, f: int | float = 1, r: int = 0) -> int | float:
    """  quadruple word from raw buffer (low order doubleword first, low order word first) to unsigned """
    return round(unpack_from('>Q', qword_swap( buf ) )[0] * f, r)


def s64be(buf: bytes, f: int | float = 1, r: int = 0) -> int | float:
    """  quadruple word from raw buffer (high to low from left to right) to signed """
    return round(unpack_from('>q', buf)[0] * f, r)


def s64le(buf: bytes, f: int | float = 1, r: int = 0) -> int | float:
    """  quadruple word from raw buffer (low order doubleword first, low order word first) to signed """
    return round(unpack_from('>q', qword_swap( buf ) )[0] * f, r)


def regs_to_str(*args) -> str:
    """ byte buffer to null-terminated utf8-string """
    buf: bytes = args[0] + b'\000'
    return buf[:buf.find(0)].decode( 'UTF8' )


def int_with_default(s: str, default_value: int = 0) -> int:
    """
    Make string to int with defaults if error or if empty

    Parameters
    ----------
    s - string to convert
    default_value - default value if ValueError or None

    Returns
    -------
    integer

    """
    if not s or s == '':
        return default_value

    try:
        return int(s)
    except ValueError:
        return default_value


def float_with_default(s: str, default_value: float = 0.) -> float:
    """
    Make string to float with defaults if error

    Parameters
    ----------
    s - string to convert
    default_value - default value if ValueError

    Returns
    -------
    float

    """
    if not s or s == '':
        return default_value
    try:
        return float(s)
    except ValueError:
        return default_value
