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
import logging

from pynetboot.packet import *

class DhcpServer(object):

	def __init__(self, ip, interface='', recv_port=67, send_port=68):
		self.ip = ip
		self.interface = interface
		self.recv_port = recv_port
		self.send_port = send_port

		logging.debug("self.raw_socket.bind((%s, 0x0800))" % self.interface)

		self.raw_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
		self.raw_socket.bind((self.interface, 0x0800))

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self.socket.setsockopt(socket.SOL_SOCKET, IN.SO_BINDTODEVICE, self.interface + '\0')

		self.socket.bind(('', self.recv_port))

	def run(self):
		self._keep_going = True

		while self._keep_going:
		
			try:
				(data, src_ip) = self.socket.recvfrom(65535)

				packet = DhcpPacket.from_wire(data)
				packet_type = packet.get_option(53, DHCP_TYPE_UINT8)

				handler_name = "handle_%s" % (DHCP_MSG_TYPE.get(packet_type, "unknown").lower())
				handler = getattr(self, handler_name, self.handle_unknown)
				handler(packet)

			except KeyboardInterrupt:
				self._keep_going = False

	def handle_unknown(self, packet):
		print >>sys.stderr, "Unknown message of type %d" % packet.get_option(53, DHCP_TYPE_UINT8)

	def send_ack(self, packet):
		ack_packet = RawDhcpPacket(packet)
		self.raw_socket.send(str(ack_packet))
		logging.info("Sent DHCPACK to %s" % DHCP_TYPE_MAC.load(packet.chaddr[:6])[1])

	def send_offer(self, packet):
		offer_pkt = RawDhcpPacket(packet)
		self.raw_socket.send(str(offer_pkt))
		logging.info("Sent DHCPOFFER to %s" % DHCP_TYPE_MAC.load(packet.chaddr[:6])[1])

class StaticDhcpServer(DhcpServer):
	def __init__(self, mac_to_ip, *args, **kwargs):
		DhcpServer.__init__(self, *args, **kwargs)
		self.mac_to_ip = mac_to_ip

	def handle_request(self, packet):
		logging.info("Handling DHCPREQUEST from %s" % DHCP_TYPE_MAC.load(packet.chaddr[:6])[1])

		ip, netmask, gateway = self.mac_to_ip[packet.chaddr[:6]]
		ack_packet = DhcpPacket()
		ack_packet.set_network(ip, netmask, gateway)
		ack_packet.join_sequence(packet.chaddr, packet.xid)

		# 'Required' Options
		ack_packet.set_option(53, 5, DHCP_TYPE_UINT8)
		ack_packet.set_option(54, self.ip, DHCP_TYPE_IPV4)

		self.send_ack(ack_packet)

	def handle_discover(self, packet):
		logging.info("Handling DHCPDISCOVER from %s" % DHCP_TYPE_MAC.load(packet.chaddr[:6])[1])

		ip, netmask, gateway = self.mac_to_ip[packet.chaddr[:6]]
		offer_packet = DhcpPacket()
		offer_packet.set_network(ip, netmask, gateway)
		offer_packet.join_sequence(packet.chaddr, packet.xid)

		# 'Required' Options
		offer_packet.set_option(53, 2, DHCP_TYPE_UINT8)
		offer_packet.set_option(54, self.ip, DHCP_TYPE_IPV4)

		self.send_offer(offer_packet)

