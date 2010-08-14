import uuid

from struct import pack, unpack
from pynetboot.constants import option_dispatcher

class DhcpPacket(object):
	
	def __init__(self, data=None, **kwargs):

		self.debug = kwargs.get("debug", False)
		self.data = data # This gets eaten quickly. Save it if you want.

		if data:
			self._parse()

	def _parse(self):
		self.op     = self._get_char()
		self.htype  = self._get_char()
		self.hlen   = self._get_char()
		self.hops   = self._get_char()
		self.xid    = self._get_u32()
		self.secs   = self._get_u16()
		self.flags  = self._get_u16()
		self.ciaddr = self._get_ip()
		self.yiaddr = self._get_ip()
		self.siaddr = self._get_ip()
		self.giaddr = self._get_ip()
		self.chaddr = self._get_mac()
		self._throw_away(10) # HELP: I'm assuming chaddr is a MAC...is that wrong?
		self.sname  = self._get_string(64)
		self.file   = self._get_string(128)

		self.cookie = self._get_hex(4) # MAGIC!
		self.options = []
	
		opt = self._get_vendor_option()
		while opt:
			if isinstance(opt, dict): # TODO: I realize that this is on the no-no list
				self.options.append(opt)
				opt = self._get_vendor_option()

# Multi-Purpose Functions	
	# {{{ _throw_away(self, num_octets)
	def _throw_away(self, num_octets):
		if self.debug:
			print "Throwing away %d octets..." % num_octets
			print " ".join([("%0X" % ord(value)) for value in self.data[0:num_octets]])
			print
	
		self.data = self.data[num_octets:]
	# }}}
	# {{{ _get_next(self, num_octets)
	def _get_next(self, num_octets):
		if self.debug:
			print "Getting %d octets..." % num_octets
			print " ".join([("%0X" % ord(value)) for value in self.data[0:num_octets]])
			print

		if len(self.data) >= num_octets:		
			data = self.data[0:num_octets]
			self.data = self.data[num_octets:]
			return data
		
		else:
			print self
	# }}}

# Specific Types (alphabetical)
	# {{{ _get_char(self)
	def _get_char(self):
		return unpack("!B", self._get_next(1))[0]
	# }}}
	# {{{ _get_char_list(self, num_octets)
	def _get_char_list(self, num_octets):
		list = []
		for i in range(num_octets):
			list.append(unpack("!B", self._get_next(1))[0])
		return "".join(map(chr, list))
	# }}}
	# {{{ _get_hex(self, num_octets)
	def _get_hex(self, num_octets):
		data = unpack("!%dc" % num_octets, self._get_next(num_octets))
		data = ["%02X" % ord(value) for value in data]
		return " ".join(data)
	# }}}
	# {{{ _get_ip(self)
	def _get_ip(self):
		info = unpack("!4c", self._get_next(4))
		info = [ord(value) for value in info]
		info = map(chr, info)
		return socket.inet_ntoa("".join(info))
	# }}}
	# {{{ _get_ip_list(self, num_octets)
	def _get_ip_list(self, num_octets):
		list = []
		for i in range(length/4):
			list.append(self._get_ip())
		return list
	# }}}
	# {{{ _get_ip_netmask_list(self, num_octets)
	def _get_ip_netmask_list(self, num_octets):
		list = []
		for i in range(length/8):
			list.append((self._get_ip(), self._get_ip()))
		return list
	# }}}
	# {{{ _get_mac(self)
	def _get_mac(self):
		data = unpack("!6c", self._get_next(6))
		data = ["%02X" % ord(value) for value in data]
		return ":".join(data)
	# }}}
	# {{{ _get_mac61(self)
	def _get_mac61(self):
		self._throw_away(1)
		return self._get_mac()
	# }}}
	# {{{ _get_type_major_minor(self)
	def _get_type_major_minor(self):
		type = self._get_char()
		major = self._get_char()
		minor = self._get_char()
		return type, major, minor
	# }}}
	# {{{ _get_string(self, num_octets)
	def _get_string(self, num_octets):
		data = unpack("!%dc" % num_octets, self._get_next(num_octets))
		data = [ord(value) for value in data]
		return "".join(map(chr, data))
	# }}}
	# {{{ _get_u16(self)
	def _get_u16(self):
		return unpack("!H", self._get_next(2))[0]
	# }}}
	# {{{ _get_u16_list(self, num_octets)
	def _get_u16_list(self, num_octets):
		list = []
		for i in range(num_octets/2):
			list.append(self._get_u16())
		return list
	# }}}
	# {{{ _get_u32(self)
	def _get_u32(self):
		return unpack("!I", self._get_next(4))[0]
	# }}}
	# {{{ _get_uuid16(self)
	def _get_uuid16(self):
		self._throw_away(1)
		return str(uuid.UUID(self._get_hex(16).replace(" ", "")))
	# }}}
	
	def __str__(self):
		return """
Headers
-------
op     : %d
htype  : %d
hlen   : %d
xid    : %d
secs   : %d
flags  : %d
ciaddr : %s
yiaddr : %s
siaddr : %s
giaddr : %s
chaddr : %s
sname  : %s
file   : %s

Vendor Options
--------------
%s""" % (self.op, self.htype, self.hlen, self.xid, self.secs, self.flags, self.ciaddr,
		self.yiaddr, self.siaddr, self.giaddr, self.chaddr, self.sname, self.file,
		"\n".join([str(opt) for opt in self.options]))

	def _get_vendor_option(self):
		type = self._get_char()

		if type != 0 and type != 255:
			length = self._get_char()
			opt = {
				"code"    : type, 
				"length"  : length,
				"content" : self._get_vendor_option_content(type, length)
			}
			return opt

		elif type == 0:
			return True

		elif type == 255:
			return False

	def _get_vendor_option_content(self, type, length):
		try:
			content = getattr(self, "_get_%s" % option_dispatcher[type]['type'])(length)
		except TypeError:
			content = getattr(self, "_get_%s" % option_dispatcher[type]['type'])()
		except Exception, e:
			print e
			content = None
			self._throw_away(length)

		return content


