import collections
import sys

import dpkt

import pynetboot


class DhcpPacket(object):
    """A single packet using the DHCP protocol."""
    MAGIC_COOKIE = "\x63\x82\x53\x63" # made of rainbow chocolate

    def __init__(self):
        """Initialize a DHCP packet."""
        self.headers = collections.OrderedDict([
            ("op", pynetboot.UInt8(default=2)), # Default to sending to client
            ("htype", pynetboot.UInt8(default=1)), # Default to Ethernet
            ("hlen", pynetboot.UInt8(default=6)), # Default to 6 byte MAC
            ("hops", pynetboot.UInt8()),
            ("xid", pynetboot.UInt32()),
            ("secs", pynetboot.UInt16()),
            ("flags", pynetboot.UInt16()),
            ("ciaddr", pynetboot.IPv4Address()),
            ("yiaddr", pynetboot.IPv4Address()),
            ("siaddr", pynetboot.IPv4Address()),
            ("giaddr", pynetboot.IPv4Address()),
            ("chaddr", pynetboot.Octets(length=16)),
            ("sname", pynetboot.String(length=64)),
            ("file", pynetboot.String(length=128)),
        ])
        self.options = collections.OrderedDict()

    def __getattr__(self, attr_name):
        """Return relevant attribute."""
        if attr_name in self.headers.keys():
            return self.headers[attr_name].value
        else:
            return object.getattr(self, attr_name)

    @classmethod
    def from_wire(cls, octets):
        """Create a packet from octets."""
        packet = cls()
        for header_name, header in packet.headers.iteritems():
            octets = header.load_octets(octets)

        octets, cookie_value = octets[4:], octets[:4]

        if cookie_value != DhcpPacket.MAGIC_COOKIE:
            raise ValueError("expecting magic cookie (RFC 1497), "
                             "got %r" % cookie_value)

        while True:
            option_code = pynetboot.UInt8()
            option_len = pynetboot.UInt8()
            octets = option_code.load_octets(octets)
            if option_code.value == 0: continue
            if option_code.value == 255: break
            octets = option_len.load_octets(octets)
            packet.options[option_code.value] = octets[:option_len.value]
            octets = octets[option_len.value:]

        return packet

    def to_wire(self):
        octets = []
        for header_name, header in self.headers.iteritems():
            octets.append(header.get_octets())

        octets.append(self.MAGIC_COOKIE)

        for option_code, option_octets in self.options.iteritems():
            code = pynetboot.UInt8()
            code.value = option_code
            option_len = pynetboot.UInt8()
            option_len.value = len(option_octets)
            octets.append(code.get_octets())
            octets.append(option_len.get_octets())
            octets.append(option_octets)

        octets.append("\xff")
        print >>sys.stderr
        print >>sys.stderr, octets
        print >>sys.stderr
        return ''.join(octets)

    def set_network(self, ip, netmask, gateway):
        self.yiaddr = ip
        self.set_option(1, netmask, IPV4)
        self.set_option(3, gateway, IPV4)

    def join_sequence(self, client_mac, xid):
        self.chaddr = client_mac
        self.xid = xid

    def set_option(self, code, value, dhcp_type=pynetboot.Octets):
        self.options[code] = dhcp_type.dump(value)

    def get_option(self, code, datavar):
        leftover = datavar.load_octets(self.options[code])
        assert not leftover
        return datavar.value


class RawDhcpPacket(object):
    def __init__(self, packet):
        u = dpkt.udp.UDP()
        u.dport = 68
        u.sport = 67
        u.data = packet.to_wire()
        u.ulen += len(u.data)

        ip_p = dpkt.ip.IP()
        ip_p.p = 17
        ip_p.dst = IPV4.dump(packet.yiaddr)
        ip_p.data = u.pack()
        ip_p.len += len(u)

        pkt = dpkt.ethernet.Ethernet()
        pkt.dst = packet.chaddr[:6]
        pkt.data = ip_p.pack()
        pkt.type = dpkt.ethernet.ETH_TYPE_IP

        self.pkt = pkt

    def __str__(self):
        return str(self.pkt)


