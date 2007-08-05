
try:
	from avahi_server import ZeroConfServer as LocalServer
	if not LocalServer.check():
		raise ImportError("Can't use avahi as it isn't running!")
	print "Using avahi ZeroConf implimentation..."
except ImportError, e:
	print e
	try:
		from bonjour_server import ZeroConfServer as LocalServer
		print "Using bonjour ZeroConf implimentation..."
	except ImportError, e:
		print e
		try:
			from pyzeroconf_server import ZeroConfServer as LocalServer
			print "Using pyZeroConf ZeroConf implimentation..."
		except ImportError, e:
			print e

from metaserver_server  import MetaServerServer  as RemoteServer
