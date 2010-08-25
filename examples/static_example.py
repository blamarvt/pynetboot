import sys
import logging

from pynetboot.server import StaticDhcpServer

logging.basicConfig(level=logging.INFO,
	stream=sys.stderr,
	format="%(levelname)8s %(name)s: %(message)s")

mac_to_ip = {
	"RT\x00\xb1\xed\xa5" : ("192.168.122.10", "255.255.255.0", "192.168.122.1")
}

server = StaticDhcpServer(mac_to_ip, "192.168.1.122", interface='virbr0')
server.run()
