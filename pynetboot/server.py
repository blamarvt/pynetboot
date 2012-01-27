# Copyright 2010 by Brian Lamar (brian.lamar@rackspace.com)
# Copyright 2010 by Nicholas VonHollen (nicholas.vonhollen@rackspace.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import socket, IN
import select
import shelve
import sys
import dpkt
import os
import logging

from pynetboot.packet import *

class DHCPServer(object):
    """Serves DHCP client requests."""

    _default_interface = ""
    _default_recv_port = 67
    _default_send_port = 68

	def __init__(self, **kwargs):
		self.interface = kwargs.get("interface", self._default_interface)
		self.recv_port = kwargs.get("recv_port", self._default_recv_port)
		self.send_port = kwargs.get("send_port", self._default_send_port)

		logging.debug("self.raw_socket.bind((%s, 0x0800))" % self.interface)

		self.raw_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
		self.raw_socket.bind((self.interface, 0x0800))

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self.socket.setsockopt(socket.SOL_SOCKET, IN.SO_BINDTODEVICE, self.interface + '\0')

		self.socket.bind(('', self.recv_port))

	def run(self):
		self._keep_going = True

		logging.info("Entering DhcpServer recv loop...")

		while self._keep_going:

			try:
				(data, src_ip) = self.socket.recvfrom(65535)

				packet = DhcpPacket.from_wire(data)
				packet_type = packet.get_option(53, UINT8)

				handler_name = "handle_%s" % (DHCP_MSG_TYPE.get(packet_type, "unknown").lower())
				handler = getattr(self, handler_name, self.handle_unknown)
				handler(packet)

			except KeyboardInterrupt:
				self._keep_going = False

	def handle_unknown(self, packet):
		print >>sys.stderr, "Unknown message of type %d" % packet.get_option(53, UINT8)

	def send_ack(self, packet):
		ack_packet = RawDhcpPacket(packet)
		self.raw_socket.send(str(ack_packet))
		logging.info("Sent DHCPACK to %s" % MAC.load(packet.chaddr[:6])[1])

	def send_offer(self, packet):
		offer_pkt = RawDhcpPacket(packet)
		self.raw_socket.send(str(offer_pkt))
		logging.info("Sent DHCPOFFER to %s" % MAC.load(packet.chaddr[:6])[1])

class GpxeDhcpServer(DhcpServer):
	def __init__(self, *args, **kwargs):
		DhcpServer.__init__(self, *args, **kwargs)

		tftp_path = kwargs.get("tftp_path", "/tftpboot")
		tftp_port = kwargs.get("tftp_port", 69)
		boot_file = kwargs.get("boot_file", "gpxelinux.0")

		ip, netmask, gateway = ("169.254.1.10","255.255.0.0","169.254.0.1")

		# Craft gPXE packet
		self.packet = DhcpPacket()
		self.packet.file = boot_file
		self.packet.siaddr = self.ip
		self.packet.set_network(ip, netmask, gateway)
		self.packet.set_option(54, self.ip, IPV4)
		self.packet.set_option(208, "\xf1\x00\x74\x7e")
		self.packet.set_option(210, "http://%s/" % self.ip, STRING)

		if os.path.exists("%s/%s" % (tftp_path, boot_file)):
			from multiprocessing import Process
			p = Process(target=self._tftp, args=(tftp_path, tftp_port))
			p.start()
		else:
			logging.warn("Not loading TFTP server (%s/%s does not exist)" % (tftp_path, boot_file))

	def _tftp(self, path, port):
		import tftpy
		self.tftp_server = tftpy.TftpServer(path)
		self.tftp_server.listen('', port)

	def handle_request(self, packet):
		logging.info("Handling DHCPREQUEST from %s" % MAC.load(packet.chaddr[:6])[1])
		self.packet.join_sequence(packet.chaddr, packet.xid)
		self.packet.set_option(53, 5, UINT8)
		self.send_ack(self.packet)

	def handle_discover(self, packet):
		logging.info("Handling DHCPDISCOVER from %s" % MAC.load(packet.chaddr[:6])[1])
		self.packet.join_sequence(packet.chaddr, packet.xid)
		self.packet.set_option(53, 2, UINT8)
		self.send_offer(self.packet)

class StaticDhcpServer(DhcpServer):
	def __init__(self, mac_to_ip, *args, **kwargs):
		DhcpServer.__init__(self, *args, **kwargs)
		self.mac_to_ip = mac_to_ip

	def handle_request(self, packet):
		logging.info("Handling DHCPREQUEST from %s" % MAC.load(packet.chaddr[:6])[1])

		ip, netmask, gateway = self.mac_to_ip[packet.chaddr[:6]]
		ack_packet = DhcpPacket()
		ack_packet.set_network(ip, netmask, gateway)
		ack_packet.join_sequence(packet.chaddr, packet.xid)

		# 'Required' Options
		ack_packet.set_option(53, 5, UINT8)
		ack_packet.set_option(54, self.ip, IPV4)

		self.send_ack(ack_packet)

	def handle_discover(self, packet):
		logging.info("Handling DHCPDISCOVER from %s" % MAC.load(packet.chaddr[:6])[1])

		ip, netmask, gateway = self.mac_to_ip[packet.chaddr[:6]]
		offer_packet = DhcpPacket()
		offer_packet.set_network(ip, netmask, gateway)
		offer_packet.join_sequence(packet.chaddr, packet.xid)

		# 'Required' Options
		offer_packet.set_option(53, 2, UINT8)
		offer_packet.set_option(54, self.ip, IPV4)

		self.send_offer(offer_packet)

