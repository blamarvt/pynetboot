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
import uuid
import socket
import string

from ctypes import create_string_buffer
from struct import pack_into, unpack
from constants import *

class DhcpPacket(object):
	
	def __init__(self, data=None, **kwargs):

		self.debug = kwargs.get("debug", False)
		self.data = data 

		self.options = {}

		if data:
			self._parse()	
	
	def getopt(self, name):
		for k, v in self.options.iteritems():
			if k == name:
				option = self.options[k]
				return self.format(option["format"], option["data"])

	def setopt(self, name, value):
		pass

	def __iter__(self):
		for header in RFC2131_HEADER:
			yield self.getopt(header[0])
	
	def __str__(self):
		return """
Headers
-------
%s

Vendor Options
--------------
%s""" % ("\n".join(["%s = %s" % (str(header), self.__getattr__(header)) for header in self.rfc_headers]), 
		"\n".join(["%s = %s" % (str(opt), self.__getattr__(opt)) for opt in self.vendor_options]))

	def _parse(self):
		offset = 0
		
		for segment in RFC2131_HEADER:
			name, obj, offset = self._get_header_data(segment, self.data, offset)
			self.options[name] = obj

		cookie = self.data[offset:offset+4]
		offset = offset + 4

		vendor_op, obj, offset = self._get_vendor_op(self.data, offset) # Prime

		while vendor_op != 255:
			self.options[vendor_op] = obj
			vendor_op, obj, offset = self._get_vendor_op(self.data, offset)

	def _get_vendor_op(self, data, offset):
		op = unpack("!B", data[offset])[0]
		
		if op not in [0, 255]:
			length = unpack("!B", data[offset+1])[0]
			offset = offset + 2
			return op, { "format" : TYPE_FORMATS[VENDOR_OPTIONS[op]], "data" : data[offset:offset+length] }, offset+length
		
		return op, None, (offset + 1)

	def _get_header_data(self, segment, data, offset):
		length = segment[1]
		return segment[0], { "format" : segment[2], "data" : data[offset:offset+length] }, offset+length

	def format(self, format_name, data):
		length = len(data)
		format = TYPE_FORMATS[format_name].replace("|", str(length))

		if "X" in format:
			format = format.replace("X", "")
			individual_len = 0
			for a in format:
				if a in range(9):
					individual_len += a
			for x in range(individual_len):
				data = unpack("!%s" % format, data)
		
		else:
			data = unpack("!%s" % format, data)

		if format_name == "mac+10extra":
			return ":".join(["%0X" % d for d in data[0:6]]) 
	
		elif format_name == "ip":
			return socket.inet_ntoa("".join([chr(octet) for octet in data]))

		elif format_name in ["rfc4578_client_id_61", "rfc4578_client_id_97"]:
			return "".join(["%0X" % d for d in data])

		return data[0]

class DhcpOfferPacket(DhcpPacket):
	def __init__(self, data=None, **kwargs):
		DhcpPacket.__init__(self, data, **kwargs)

		self.op = 2
		self.yiaddr = 
