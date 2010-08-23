# Copyright 2010 by Brian Lamar
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

from packet import *
from constants import *

# Thanks to Microsoft for http://support.microsoft.com/kb/169289

class DhcpServer(object):

	def __init__(self, interface='', recv_port=67, send_port=68):
		self.interface = interface
		self.recv_port = recv_port
		self.send_port = send_port
		self.db = shelve.open('pynetboot.db')		

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self.socket.setsockopt(socket.SOL_SOCKET, IN.SO_BINDTODEVICE, self.interface + '\0')

		self.socket.bind(('', self.recv_port))

	def run(self):
		self._keep_going = True

		while self._keep_going:
		
			try:
				input, _ , _ = select.select([self.socket],[],[])
				(data, src_ip) = self.socket.recvfrom(65535)

				packet = DhcpPacket(data)

				if packet.op == DHCPDISCOVER:
					self.handle_discover(packet)
	
				elif packet.op == DHCPREQUEST:
					self.handle_request(packet)

				elif packet.op == DHCPDECLINE:
					self.handle_decline(packet)
	
				elif packet.op == DHCPRELEASE:
					self.handle_release(packet)

				else:
					# DHCPINFORM and others that we don't currently support
					self.handle_unknown(packet) 

			except KeyboardInterrupt:
				self._keep_going = False

	def handle_discover(self, in_pkt):
		try:
			self.send(DhcpOfferPacket(in_pkt.data))
		except Exception, e:
			import traceback
			traceback.print_exc()
			print "Not offering due to %s" % type(e)

	def handle_request(self, pkt):
		pass

	def handle_decline(self, pkt):
		pass

	def handle_release(self, pkt):
		pass

	def handle_unknown(self, pkt):
		pass

	def send(self, pkt):
		data = list(pkt)
		print data
		self.socket.sendto("".join(data), 0, ('<broadcast>', self.send_port))

if __name__ == "__main__":
	server = DhcpServer()
	server.run()
