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

option_dispatcher = {
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
	57 : {
		'type' : 'u16',
		'name' : 'max_dhcp_message_size'
	},
	60 : {
		'type' : 'char_list',
		'name' : 'vendor_class_id'
	},
	61 : {
		'type' : 'mac61',
		'name' : 'client_uuid_61'
	},
	94 : {
		'type' : 'type_major_minor',
		'name' : 'client_nic_id'
	},
	97 : {
		'type' : 'uuid16',
		'name' : 'client_uuid_97'
	}
}
