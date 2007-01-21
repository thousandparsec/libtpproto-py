#!/usr/bin/env python

from tp.netlib import version
version = "%s.%s.%s" % version

from setuptools import setup

setup(
	name		="libtpproto-py",
	version		=version,
	license		="LGPL",
	description	="Network library for Thousand Parsec",
	long_description="""\
A library of code for both Servers and Clients to support the Thousand Parsec 
protocol. 

Includes support for:
	* Both non-blocking and blocking usage
	* Version 3 protocol
	* HTTP/HTTPS Tunneling
	* Generic Reference System
""",
	author		="Tim Ansell",
	author_email="tim@thousandparsec.net",
	url			="http://www.thousandparsec.net",
	keywords	="thousand parsec space network empire building strategy game",

	namespace_packages = ['tp'],
	packages=[ \
		'tp',
		'tp.netlib',
		'tp.netlib.objects',
		'tp.netlib.objects.ObjectExtra',
		'tp.netlib.objects.OrderExtra',
		'tp.netlib.support',
		],
)
