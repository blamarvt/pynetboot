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
#
# Helpful Link: http://www.networksorcery.com/enp/protocol/bootp/options.htm 

DHCPDISCOVER = 1
DHCPOFFER = 2
DHCPREQUEST = 3
DHCPACK = 4
DHCPNAK = 5

TYPE_FORMATS = {
	'ip'     : '4B',
	'char'   : 'B',
	's32'    : 'i',
	'u32'    : 'I',
	's16'    : 'h',
	'u16'    : 'H',
	'bool'   : '?',
	'mac'    : '6B',
	'mac+10extra'      : '16B',
	'type_major_minor' : '3B',

	# Custom Formats (not to be used with pack_into/unpack)
	'string'          : '|c',
	'ip_list'         : '4cX', 
	'ip_netmask_list' : '8cX', 
	'u16_list'        : 'HX', 
	'char_list'       : 'BX',

	# Really special...and sometimes confusing...
	'rfc4578_client_id_61' : '|B',
	'rfc4578_client_id_97' : '|B',
	'user_class_data'      : '|B',
	'etherboot'            : '|B',
	'parameter_list'       : '|B',
}

RFC2131_HEADER = [
	['op',      1, 'char'],
	['htype',   1, 'char'],
	['hlen',    1, 'char'],
	['hops',    1, 'char'],
	['xid',     4, 'u32'],
	['secs',    2, 'u16'],
	['flags',   2, 'u16'],
	['ciaddr',  4, 'ip'],
	['yiaddr',  4, 'ip'],
	['siaddr',  4, 'ip'],
	['giaddr',  4, 'ip'],
	['chaddr', 16, 'mac+10extra'],
	['sname',  64, 'string'],
	['file',  128, 'string']
]

VENDOR_OPTIONS = {
	1 : {
		'type' : 'ip',
		'name' : 'subnet_mask'
	},
	2 : {
		'type' : 's32',
		'name' : 'time_offset' # May be deprecated
	},
	3 : {
		'type' : 'ip_list',
		'name' : 'router'
	},
	4 : {
		'type' : 'ip_list',
		'name' : 'time_server'
	},
	5 : {
		'type' : 'ip_list',
		'name' : 'name_server'
	},
	6 : {
		'type' : 'ip_list',
		'name' : 'dns_server'
	},
	7 : {
		'type' : 'ip_list',
		'name' : 'log_server'
	},
	8 : {
		'type' : 'ip_list',
		'name' : 'quote_server'
	},
	9 : {
		'type' : 'ip_list',
		'name' : 'lpr_server'
	},
	10 : {
		'type' : 'ip_list',
		'name' : 'impress_server'
	},
	11 : {
		'type' : 'ip_list',
		'name' : 'resource_location_server'
	},
	12 : {
		'type' : 'string',
		'name' : 'hostname'
	},
	13 : {
		'type' : 'u16',
		'name' : 'boot_file_size'
	},
	14 : {
		'type' : 'string',
		'name' : 'merit_dump_file'
	},
	15 : {
		'type' : 'string',
		'name' : 'domain_name'
	},
	16 : {
		'type' : 'ip',
		'name' : 'swap_server'
	},
	17 : {
		'type' : 'string',
		'name' : 'root_path'
	},
	18 : {
		'type' : 'string',
		'name' : 'extensions_path'
	},
	19 : {
		'type' : 'bool',
		'name' : 'ip_forwarding'
	},
	20 : {
		'type' : 'bool',
		'name' : 'non-local_source_routing'
	},
	21 : {
		'type' : 'ip_netmask_list',
		'name' : 'policy_filter'
	},
	22 : {
		'type' : 'u16',
		'name' : 'max_reassembly_size'
	},
	23 : {
		'type' : 'char',
		'name' : 'default_ip_ttl'
	},
	24 : {
		'type' : 'u32',
		'name' : 'path_mtu_aging_timeout'
	},
	25 : {
		'type' : 'u16_list',
		'name' : 'path_mtu_plateau_table'
	},
	26 : {
		'type' : 'u16',
		'name' : 'interface_mtu'
	},
	27 : {
		'type' : 'bool',
		'name' : 'all_subnets_are_local'
	},
	28 : {
		'type' : 'ip',
		'name' : 'broadcast_address'
	},
	29 : {
		'type' : 'bool',
		'name' : 'perform_mask_discovery'
	},
	30 : {
		'type' : 'bool',
		'name' : 'mask_supplier'
	},
	53 : {
		'type' : 'char',
		'name' : 'dhcp_message_type'
	},
	55 : {
		'type' : 'parameter_list',
		'name' : 'parameter_list_request'
	},
	57 : {
		'type' : 'u16',
		'name' : 'max_dhcp_message_size'
	},
	60 : {
		'type' : 'char_list',
		'name' : 'vendor_class_id'
	},
	61 : {
		'type' : 'rfc4578_client_id_61',
		'name' : 'rfc4578_client_id_61'
	},
	77 : {
		'type' : 'user_class_data',
		'name' : 'user_class_data'
	},
	93 : {
		'type' : 'u16',
		'name' : 'client_arch'
	},
	94 : {
		'type' : 'type_major_minor',
		'name' : 'client_nic_id'
	},
	97 : {
		'type' : 'rfc4578_client_id_97',
		'name' : 'rfc4578_client_id_97'
	},
	175 : {
		'type' : 'etherboot',
		'name' : 'etherboot'
	}
}
