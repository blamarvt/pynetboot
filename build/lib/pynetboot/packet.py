import dpkt

from pynetboot.types import *

_dhcp_headers = [
	("op", DHCP_TYPE_UINT8, 2), # Default to sending to client (2)
	("htype", DHCP_TYPE_UINT8, 1), # Default to Ethernet
	("hlen", DHCP_TYPE_UINT8, 6), # Default to 6 byte MAC
	("hops", DHCP_TYPE_UINT8),   
	("xid", DHCP_TYPE_UINT32),
	("secs", DHCP_TYPE_UINT16),
	("flags", DHCP_TYPE_UINT16),
	("ciaddr", DHCP_TYPE_IPV4),
	("yiaddr", DHCP_TYPE_IPV4),
	("siaddr", DHCP_TYPE_IPV4),
	("giaddr", DHCP_TYPE_IPV4),
	("chaddr", DhcpOctetsType(16)),
	("sname", DhcpStringType(64)),
	("file", DhcpStringType(128)),
]

_dhcp_headers = map(lambda args: DhcpHeader(*args), _dhcp_headers)

class DhcpPacket(object):
	MAGIC_COOKIE = "\x63\x82\x53\x63" # made of rainbow chocolate

	@classmethod
	def from_wire(cls, octets):
		self = cls()
		for header_def in _dhcp_headers:
			octets, value = header_def.load(octets)
			self._headers[header_def.name] = value
		
		octets, cookie_value = octets[4:], octets[:4]
		if cookie_value != self.MAGIC_COOKIE:
			raise ValueError("expecting dhcp/bootp magic cookie (RFC 1497), got %r" % cookie_value)
		
		while True:
			octets, option_code = DHCP_TYPE_UINT8.load(octets)
			if option_code == 0:
				continue
			elif option_code == 255:
				break
			
			octets, option_len = DHCP_TYPE_UINT8.load(octets)
			octets, option_octets = octets[option_len:], octets[:option_len]
			self._options[option_code] = option_octets
			
		return self

	def __init__(self):
		self._headers = {}
		self._options = {}

		for header_def in _dhcp_headers:
			self._headers[header_def.name] = header_def.default_value

	def to_wire(self):
		octets = []
		for header_def in _dhcp_headers:
			value = self._headers[header_def.name]
			octets.append(header_def.dump(value))
		
		octets.append(self.MAGIC_COOKIE)

		for option_code, option_octets in self._options.iteritems():
			octets.append(DHCP_TYPE_UINT8.dump(option_code))
			octets.append(DHCP_TYPE_UINT8.dump(len(option_octets)))
			octets.append(option_octets)
		
		octets.append("\xff")
		return ''.join(octets)

	def set_network(self, ip, netmask, gateway):
		self.yiaddr = ip
		self.set_option(1, netmask, DHCP_TYPE_IPV4)
		self.set_option(3, gateway, DHCP_TYPE_IPV4)

	def join_sequence(self, client_mac, xid):
		self.chaddr = client_mac
		self.xid = xid

	def set_option(self, code, value, dhcp_type=DHCP_TYPE_OCTETS):
		self._options[code] = dhcp_type.dump(value)

	def get_option(self, code, dhcp_type=DHCP_TYPE_OCTETS):
		leftover, value = dhcp_type.load(self._options[code])
		assert not leftover
		return value

for _header_def in _dhcp_headers:
	setattr(DhcpPacket, _header_def.name, _header_def)

class RawDhcpPacket(object):
	def __init__(self, packet):
		u = dpkt.udp.UDP()
		u.dport = 68
		u.sport = 67
		u.data = packet.to_wire()
		u.ulen += len(u.data)

		ip_p = dpkt.ip.IP()
		ip_p.p = 17
		ip_p.dst = DHCP_TYPE_IPV4.dump(packet.yiaddr)
		ip_p.data = u.pack()
		ip_p.len += len(u)

		pkt = dpkt.ethernet.Ethernet()
		pkt.dst = packet.chaddr[:6]
		pkt.data = ip_p.pack()
		pkt.type = dpkt.ethernet.ETH_TYPE_IP

		self.pkt = pkt

	def __str__(self):
		return str(self.pkt)

import unittest
class TestDhcpPacket(unittest.TestCase):
	def testPacket(self):
		octets = open('dhcp_discover').read()
		p = DhcpPacket.from_wire(octets)
		self.assertEquals(p.op, 1)
		self.assertEquals(p.htype, 1)
		self.assertEquals(p.hlen, 6)
		self.assertEquals(p.hops, 0)
		self.assertEquals(p.ciaddr, "0.0.0.0")
		self.assertEquals(p.get_option(53, DHCP_TYPE_UINT8), 1)
		self.assertEquals(p.get_option(93, DHCP_TYPE_UINT16), 0)
		self.assertEquals(p.get_option(60, DHCP_TYPE_STRING), "PXEClient:Arch:00000:UNDI:002001")
		
		# Serialize and unserialize a packet, then check against original
		p2 = DhcpPacket.from_wire(p.to_wire())
		for header_def in _dhcp_headers:
			self.assertEquals(getattr(p, header_def.name), getattr(p2, header_def.name))
		self.assertEquals(p._options, p2._options)
