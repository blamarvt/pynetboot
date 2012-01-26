import socket
import struct


class DhcpHeader(object):
    def __init__(self, name, datatype, default=None):
        self.name = name
        self.default = default
        self.datatype = datatype

    def load(self, encoded_value):
        return self.datatype.load(encoded_value)

    def dump(self, value):
        return self.datatype.dump(value)

    @property
    def default_value(self):
        return self.default or self.datatype.default_value

    def __get__(self, obj, _):
        return obj._headers[self.name]

    def __set__(self, obj, value):
        obj._headers[self.name] = value


class Data(object):
    """Base data class."""
    _default_value = None

    def __init__(self, default=None):
        """Initialize data."""
        self.value = default or self._default_value

    def get_octets(self):
        """Return the formatted value of this data."""
        return self.value


class Struct(Data):
    """Struct-based data type."""
    _struct_format = None

    def __init__(self, default=None):
        """Initialize struct-like data."""
        Data.__init__(self, default)
        self._struct = struct.Struct("!" + self._struct_format)

    def get_octets(self):
        """Return the formatted value of this data."""
        return self._struct.pack(self.value)

    def load_octets(self, octets):
        """Load data from a set of octets."""
        length = self._struct.size
        leftover, octets = octets[length:], octets[:length]
        self.value = self._struct.unpack(octets)[0]
        return leftover


class Int8(Struct):
    _struct_format = "b"


class UInt8(Struct):
    _struct_format = "B"


class Int16(Struct):
    _struct_format = "h"


class UInt16(Struct):
    _struct_format = "H"


class Int32(Struct):
    _struct_format = "i"


class UInt32(Struct):
    _struct_format = "I"


class IPv4Address(Data):
    """IP version 4 data."""
    _default_value = "0.0.0.0"

    def get_octets(self):
        """Return the formatted value of this data."""
        return socket.inet_aton(self.value)

    def load_octets(self, octets):
        """Load data from a set of octets."""
        leftover, ip_octets = octets[4:], octets[:4]
        self.value = socket.inet_ntoa(ip_octets)
        return leftover


class Octets(Data):
    """Raw octet data."""

    def __init__(self, length, default=None):
        """Initialize raw octet data."""
        self._length = length
        self._default_value = default or "\0" * (self._length)
        Data.__init__(self, default)

    def load_octets(self, octets):
        """Load data from a set of octets."""
        self.value = octets[:self._length]
        return octets[self._length:]


class MAC(Data):
    """Machine address control data."""
    _default_value = "00:00:00:00:00"

    def load_octets(self, octets):
        """Load MAC from octets."""
        leftover, mac = octets[6:], octets[:6]
        mac = ["%0.2X" % struct.unpack("B", octet)[0] for octet in mac]
        self.value = ":".join(mac)
        return leftover

    def get_octets(self):
        """Retrieve MAC as a set of octets."""
        m = [int(v) for v in self.value.split(":")]
        return struct.pack("6B", m[0], m[1], m[2], m[3], m[4], m[5])


class String(Data):
    _default_value = ""

    def __init__(self, length, default=None):
        """Initialize string data."""
        self._length = length
        Data.__init__(self, default)

    def load_octets(self, octets):
        """Load a string from octets."""
        raw_value = octets[:self._length]
        leftover = octets[self._length:]
        idx = raw_value.find("\0")
        if idx == -1:
            self.value = raw_value
        else:
            self.value = raw_value[:idx]
        return leftover

    def get_octets(self):
        """Retrieve a string in octet form."""
        return self.value.ljust(self._length, "\0")


DHCP_MSG_TYPE = {
    1 : "DISCOVER",
    2 : "OFFER",
    3 : "REQUEST",
    4 : "DECLINE",
    5 : "ACK",
    6 : "NAK",
    7 : "RELEASE",
    8 : "INFORM"
}
