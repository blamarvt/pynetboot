#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
	name         = 'pynetboot',
	version      = '0.2a',
	description  = 'Python DHCP server specifically designed to be used with gPXE for network booting',
	author       = 'Brian Lamar',
	author_email = 'brian.lamar@rackspace.com',
	url          = 'http://www.pynetboot.com',
	packages     = find_packages()
)
