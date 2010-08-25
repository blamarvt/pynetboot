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

class DhcpDataType(object):
	def load(self, octets):
		raise NotImplementedError(octets)

	def dump(self, value):
		raise NotImplementedError(value)

class DhcpStructType(DhcpDataType):
	def __init__(self, format, default_value=0):
		self._struct = struct.Struct("!" + format)
		self.default_value = default_value

	def load(self, octets, length=None):
		length = length or self._struct.size
		if length != self._struct.size:
			raise ValueError("length must be %d or not given" % self._struct.size)
		leftover, octets = octets[self._struct.size:], octets[:self._struct.size]
		value = self._struct.unpack(octets)[0]
		return leftover, value

	def dump(self, value):
		return self._struct.pack(value)

class DhcpIpType(DhcpDataType):	
	IP_NUM_BYTES = 4
	default_value = "0.0.0.0"

	def load(self, octets, length=4):
		if length != 4:
			raise ValueError("length must be 4 or not given")
		leftover, ip_octets = octets[self.IP_NUM_BYTES:], octets[:self.IP_NUM_BYTES]
		value = socket.inet_ntoa(ip_octets)
		return leftover, value

	def dump(self, value):
		return socket.inet_aton(value)

class DhcpOctetsType(DhcpDataType):
	def __init__(self, num_octets=None):
		self._num_octets = num_octets
		self.default_value = "\0" * (self._num_octets or 0)

	def load(self, octets, length=None):
		length = self._num_octets or length or 0
		return octets[length:], octets[:length]

	def dump(self, value):
		if len(value) != self._num_octets:
			raise ValueError("value must be exactly %d octets" % self._num_octets)
		return value

class DhcpMacType(DhcpDataType):
	MAC_NUM_BYTES = 6
	default_value = "00:00:00:00:00"

	def load(self, octets, length=6):
		if length != 6:
			raise ValueError("length must be 6 or not given")
		leftover, mac_octets = octets[self.MAC_NUM_BYTES:], octets[:self.MAC_NUM_BYTES]
		value = ":".join(["%0.2X" % struct.unpack("B", octet)[0] for octet in mac_octets])
		return leftover, value

	def dump(self, value):
		m = [int(v) for v in value.split(":")]
		return struct.pack("6B", m[0], m[1], m[2], m[3], m[4], m[5])

class DhcpStringType(DhcpOctetsType):
	def __init__(self, num_octets=None):
		DhcpOctetsType.__init__(self, num_octets)
		self.default_value = ""

	def load(self, octets, length=None):
		leftover, value = DhcpOctetsType.load(self, octets, length or len(octets))
		idx = value.find("\0")
		if idx == -1:
			return leftover, value
		else:
			return leftover, value[:idx]

	def dump(self, value):
		if self._num_octets is not None:
			if len(value) > self._num_octets:
				raise ValueError("value must be less than or equal to %d octets" % self._num_octets)
			value = value.ljust(self._num_octets, "\0")
		return DhcpOctetsType.dump(self, value)

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

DHCP_TYPE_INT8 = DhcpStructType("b")
DHCP_TYPE_UINT8 = DhcpStructType("B")
DHCP_TYPE_INT16 = DhcpStructType("h")
DHCP_TYPE_UINT16 = DhcpStructType("H")
DHCP_TYPE_INT32 = DhcpStructType("i")
DHCP_TYPE_UINT32 = DhcpStructType("I")
DHCP_TYPE_MAC = DhcpMacType()
DHCP_TYPE_STRING = DhcpStringType()
DHCP_TYPE_OCTETS = DhcpOctetsType()
DHCP_TYPE_IPV4 = DhcpIpType()

