#!/usr/bin/env python

from distutils.core import setup

from __init__ import version
version = "%s.%s.%s" % version

import os.path
import os

if os.path.exists('CVS'):
	base = ['LICENSE']
	for file in base:
		if os.path.exists(file):
			os.unlink(file)
		print "Getting %s" % file
		os.link(os.path.join('..', file), file)
		

setup(name="py-netlib",
	version=version,
	description="Network library for Thousand Parsec",
	author="Tim Ansell",
	author_email="tim@thousandparsec.net",
	url="http://www.thousandparsec.net",
	packages=[ \
		'tp',
		'tp.netlib',
		'tp.netlib.objects',
		'tp.netlib.objects.ObjectExtra',
		'tp.netlib.objects.OrderExtra',
		'tp.netlib.support',
		'tp.netlib.tests',
		'tp.netlib.tests.python',
		'tp.netlib.tests.client',
		'tp.netlib.tests.server',
		],
	package_dir = {'tp.netlib': '', 'tp': 'empty'}
)

