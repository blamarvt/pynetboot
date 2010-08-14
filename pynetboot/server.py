import socket, IN
import select

from pynetboot.packet import DhcpPacket
from pynetboot.lease import DhcpLease

# Thanks to Microsoft for http://support.microsoft.com/kb/169289

class DhcpServer(object):

	def __init__(self, interface='', port=67):
		self.interface = interface
		self.port = port
		self.db = shelve.open('pynetboot.db')		

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self.socket.setsockopt(socket.SOL_SOCKET, IN.SO_BINDTODEVICE, self.interface + '\0')

		self.socket.bind(('', self.port))

	def run(self):
		self._keep_going = True

		while self._keep_going:
		
			try:
				input, _ , _ = select.select([self.socket],[],[])
				(data, src_ip) = self.socket.recvfrom(65535)
				packet = DhcpPacket(data)

				if packet.type == p_types.DHCPDISCOVER:
					self.handle_discover(packet)
	
				elif packet.type == p_types.DHCPREQUEST:
					self.handle_request(packet)

				elif packet.type == p_types.DHCPDECLINE:
					self.handle_decline(packet)
	
				elif packet.type == p_types.DHCPRELEASE:
					self.handle_release(packet)

				else:
					# DHCPINFORM and others that we don't currently support
					self.handle_unknown(packet) 

			except KeyboardInterrupt:
				self._keep_going = False

		def handle_discover(in_pkt):
			out_pkt = DhcpPacket()
			out_pkt.op = p_types.DHCPOFFER
			out_pkt.yiaddr = 
		def handle_request(pkt):
			pass

		def handle_decline(pkt):
			pass

		def handle_release(pkt):
			pass

		def handle_unknown(pkt):
			pass

if __name__ == "__main__":
	server = DhcpServer()
	server.run()
