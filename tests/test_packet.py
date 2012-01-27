import os
import unittest

import pynetboot.packet
import pynetboot.types


DIR = os.path.dirname(__file__)


class TestPacket(unittest.TestCase):

    def testPacket(self):
        octets = open("%s/testdata/dhcp_discover" % DIR).read()
        p = pynetboot.packet.DhcpPacket.from_wire(octets)
        self.assertEquals(p.op, 1)
        self.assertEquals(p.htype, 1)
        self.assertEquals(p.hlen, 6)
        self.assertEquals(p.hops, 0)
        self.assertEquals(p.ciaddr, "0.0.0.0")
        self.assertEquals(p.get_option(53, pynetboot.UInt8()), 1)
        self.assertEquals(p.get_option(93, pynetboot.UInt16()), 0)
        self.assertEquals(p.get_option(60, pynetboot.String(length=32)),
                          "PXEClient:Arch:00000:UNDI:002001")

        # Serialize and unserialize a packet, then check against original
        p2 = pynetboot.packet.DhcpPacket.from_wire(p.to_wire())
        for header_name, header in p2.headers.iteritems():
            self.assertEquals(getattr(p, header_name), getattr(p2, header_name))
        self.assertEquals(p.options, p2.options)
