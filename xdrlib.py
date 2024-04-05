"""Implements (a subset of) Sun XDR -- eXternal Data Representation.

See: RFC 1014

"""

from io import BytesIO
from functools import wraps
import struct
import typing
import warnings

# Package version
__version__ = "4.0.2"


# Control * exports.
__all__ = ["Error", "Packer", "Unpacker", "ConversionError"]


# Exceptions
class Error(Exception):
    """Exception class for this module. Use:

    except xdrlib.Error as var:
        # var has the Error instance for the exception

    Public ivars:
        msg -- contains the message

    """
    def __init__(self, msg):
        self.msg = msg
    def __repr__(self):
        return repr(self.msg)
    def __str__(self):
        return str(self.msg)


class ConversionError(Error):
    """Error during conversion to or from XDR format."""


def raise_conversion_error(function):
    """ Wrap any raised struct.errors in a ConversionError. """

    @wraps(function)
    def result(self, value):
        try:
            return function(self, value)
        except struct.error as e:
            raise ConversionError(e.args[0]) from None
    return result


class Packer:
    """Pack various data representations into a buffer."""

    def __init__(self):
        """Create an XDR "packer" that can encode Python data into XDR format."""
        self.reset()

    def reset(self):
        """Reset the internal buffer for packed data."""
        self.__buf = BytesIO()

    def get_buffer(self) -> bytes:
        """Return the packed data."""
        return self.__buf.getvalue()

    def get_buf(self) -> bytes:
        """(Deprecated) Return the packed data.

        This function is deprecated.  Use get_buffer() instead."""

        warnings.warn("xdrlib.Packet.get_buf() is deprecated. Use get_buffer() instead",
                      DeprecationWarning)

        return self.get_buffer()

    @raise_conversion_error
    def pack_uint(self, x: int):
        """Pack a 32-bit unsigned integer value."""
        self.__buf.write(struct.pack('>L', x))

    @raise_conversion_error
    def pack_int(self, x: int):
        """Pack a 32-bit signed integer value."""
        self.__buf.write(struct.pack('>l', x))

    def pack_enum(self, x: int):
        """Pack an enumeration value."""
        self.pack_int(x)

    def pack_bool(self, x: typing.Any):
        """Pack a boolean value."""
        if x:
            self.__buf.write(b'\0\0\0\1')
        else:
            self.__buf.write(b'\0\0\0\0')

    @raise_conversion_error
    def pack_uhyper(self, x: int):
        """Pack a 64-bit unsigned integer value."""
        self.__buf.write(struct.pack(">Q", x))

    @raise_conversion_error
    def pack_hyper(self, x: int):
        """Pack a 64-bit signed integer value."""
        self.__buf.write(struct.pack(">q", x))

    @raise_conversion_error
    def pack_float(self, x: float):
        """Pack a 32-bit (single-precision) floating point value."""
        self.__buf.write(struct.pack('>f', x))

    @raise_conversion_error
    def pack_double(self, x: float):
        """Pack a 64-bit (double-precision) floating point value."""
        self.__buf.write(struct.pack('>d', x))

    def pack_fstring(self, length: int, data: bytes):
        """Pack a fixed-size string value.

        In XDR, the "string" type has no real distinction from
        the opaque type.  Both are a sequence of bytes.  When
        writing a Python string, it should be encoded first,
        typically as UTF-8.

        packer.pack_fstring(7, str_value.encode("UTF-8"))

        A fixed string value has a fixed length, pre-defined and
        known to both sender and receiver.  The length is not sent
        over the wire, just the data bytes.

        :param length: size of the input, in bytes
        :param data: bytes value, at least "length" bytes long"""

        return self.pack_fopaque(length, data)

    def pack_fopaque(self, length: int, data: bytes):
        """Pack a fixed-size byte buffer value.

        A fixed opaque value has a fixed length, pre-defined and
        known to both sender and receiver.  The length is not sent
        over the wire, just the data bytes.

        :param length: size of the input, in bytes
        :param data: bytes value"""

        if length < 0:
            raise ValueError(f"data size {length} must not "
                             "be negative")
        if len(data) < length:
            raise ValueError(f"data size {len(data)} less than "
                             f"specified size {length}")

        data = data[:length]
        length = ((length + 3) // 4) * 4
        data = data + (length - len(data)) * b'\0'
        self.__buf.write(data)

    def pack_opaque(self, data: bytes):
        """Pack an opaque value.

        An XDR opaque value is a sequence of uninterpreted bytes.

        :param data: bytes value to pack."""
        length = len(data)
        self.pack_uint(length)
        self.pack_fstring(length, data)

    def pack_string(self, data: bytes):
        """Pack a string value.

        In XDR, the "string" type has no real distinction from
        the opaque type.  Both are a sequence of bytes.  When
        writing a Python string, it should be encoded first,
        typically as UTF-8.

        packer.pack_string(str_value.encode("UTF-8"))

        An XDR variable-length string value is encoded on the
        wire as a 32-bit integer length prior to the contents
        of the string itself.

        :param data: bytes value to pack"""
        self.pack_opaque(data)

    def pack_bytes(self, data: bytes):
        """Pack a Python bytes value.

        Bytes values are packed as an XDR opaque.

        :param data: bytes value to pack."""
        self.pack_opaque(data)


    def pack_list(self,
                  seq: typing.Sequence,
                  pack_item: typing.Callable):
        """Pack a list of items.

        :param seq: List of items to be packed
        :param pack_item: Function to use to pack items"""
        for item in seq:
            self.pack_uint(1)
            pack_item(item)
        self.pack_uint(0)

    def pack_farray(self, length: int,
                    seq: typing.Sequence,
                    pack_item: typing.Callable):
        """Pack a fixed-size array of items.

        :param length: Integer number of items
        :param seq: List of items to be packed
        :param pack_item: Function to use to pack items"""
        if len(seq) != length:
            raise ValueError('wrong array size')
        for item in seq:
            pack_item(item)

    def pack_array(self,
                   seq: typing.Sequence,
                   pack_item: typing.Callable):
        """Pack a variable-length array of items.

        :param seq: List of items to be packed
        :param pack_item: Function to use to pack items"""
        length = len(seq)
        self.pack_uint(length)
        self.pack_farray(length, seq, pack_item)


class Unpacker:
    """Unpacks various data representations from the given buffer."""

    def __init__(self, data: bytes):
        """Create an XDR decoder for the supplied buffer."""
        self.__buf = data
        self.__pos = 0

    def reset(self, data):
        """Reset the XDR decoder.

        :param data: Bytes buffer to be decoded"""
        self.__buf = data
        self.__pos = 0

    def get_position(self) -> int:
        """Return the current offset within the decoding buffer."""
        return self.__pos

    def set_position(self, position: int):
        """Set the position within the decoding buffer.

        :param position: Integer offset of next position to be decoded from the buffer."""
        self.__pos = position

    def get_buffer(self) -> bytes:
        """Return the complete internal buffer to be decoded."""
        return self.__buf

    def done(self):
        """Assert that the decoding is complete."""
        if self.__pos < len(self.__buf):
            raise Error('unextracted data remains')

    def unpack_uint(self) -> int:
        """Decode a 32-bit unsigned integer value at the current position.

        Advances the internal position by 4 octets."""
        i = self.__pos
        self.__pos = j = i + 4
        data = self.__buf[i:j]
        if len(data) < 4:
            raise EOFError
        return struct.unpack('>L', data)[0]

    def unpack_int(self) -> int:
        """Decode a 32-bit signed integer value at the current position.

        Advances the internal position by 4 octets."""
        i = self.__pos
        self.__pos = j = i + 4
        data = self.__buf[i:j]
        if len(data) < 4:
            raise EOFError
        return struct.unpack('>l', data)[0]

    def unpack_enum(self) -> int:
        """Decode an enumeration value.

        Advances the internal position by 4 octets."""
        return self.unpack_int()

    def unpack_bool(self) -> bool:
        """Decode a boolean value at the current position.

        Advances the internal position by 4 octets."""
        return bool(self.unpack_int())

    def unpack_uhyper(self) -> int:
        """Decode a 64 bit unsigned integer value at the current position.

        Advances the internal position by 8 octets."""
        i = self.__pos
        self.__pos = j = i + 8
        data = self.__buf[i:j]
        if len(data) < 8:
            raise EOFError
        return struct.unpack('>Q', data)[0]

    def unpack_hyper(self) -> int:
        """Decode a 64 bit signed integer value at the current position.

        Advances the internal position by 8 octets."""
        i = self.__pos
        self.__pos = j = i + 8
        data = self.__buf[i:j]
        if len(data) < 8:
            raise EOFError
        return struct.unpack('>q', data)[0]

    def unpack_float(self) -> float:
        """Decode a 32-bit (single precision) floating point value at the current position.

        Advances the internal position by 4 octets."""
        i = self.__pos
        self.__pos = j = i+4
        data = self.__buf[i:j]
        if len(data) < 4:
            raise EOFError
        return struct.unpack('>f', data)[0]

    def unpack_double(self) -> float:
        """Decode a 364-bit (double precision) floating point value at the current position.

        Advances the internal position by 4 octets."""
        i = self.__pos
        self.__pos = j = i+8
        data = self.__buf[i:j]
        if len(data) < 8:
            raise EOFError
        return struct.unpack('>d', data)[0]

    def unpack_fstring(self, n: int):
        """Decode a fixed-length string at the current position."""
        if n < 0:
            raise ValueError('fstring size must be nonnegative')
        i = self.__pos
        j = i + (n+3)//4*4
        if j > len(self.__buf):
            raise EOFError
        self.__pos = j
        return self.__buf[i:i+n]

    unpack_fopaque = unpack_fstring

    def unpack_string(self):
        """Decode a variable-length string from the current position."""
        n = self.unpack_uint()
        return self.unpack_fstring(n)

    unpack_opaque = unpack_string
    unpack_bytes = unpack_string

    def unpack_list(self, unpack_item: typing.Callable) -> typing.Sequence:
        """Decode a variable-length list.

        :param unpack_item: Function to decode items"""
        seq = []
        while 1:
            x = self.unpack_uint()
            if x == 0:
                break
            if x != 1:
                raise ConversionError(f"0 or 1 expected, got {x}")
            item = unpack_item()
            seq.append(item)
        return seq

    def unpack_farray(self, n: int, unpack_item: typing.Callable) -> typing.Sequence:
        """Decode fixed-length array.

        :param n: Integer number of elements
        :param unpack_item: Function to decode items"""
        seq = []
        for i in range(n):
            seq.append(unpack_item())
        return seq

    def unpack_array(self, unpack_item: typing.Callable) -> typing.Sequence:
        """Decode array of items.

        :param unpack_item: Function to unpack array elements"""
        n = self.unpack_uint()
        return self.unpack_farray(n, unpack_item)
