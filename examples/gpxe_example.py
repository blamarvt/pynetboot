import sys
import logging

from pynetboot.server import GpxeDhcpServer

logging.basicConfig(level=logging.INFO,
	stream=sys.stderr,
	format="%(levelname)8s %(name)s: %(message)s")

server = GpxeDhcpServer("169.254.0.1", interface='virbr0')
server.run()
