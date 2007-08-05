
try:
	from avahi_browser import ZeroConfBrowser as LocalBrowser
	if not LocalBrowser.check():
		raise ImportError("Can't use avahi as it isn't running!")
	print "Using avahi ZeroConf implimentation..."
except ImportError, e:
	print e
	try:
		from bonjour_browser import ZeroConfBrowser as LocalBrowser
		print "Using bonjour ZeroConf implimentation..."
	except ImportError, e:
		print e
		try:
			from pyzeroconf_browser import ZeroConfBrowser as LocalBrowser
			print "Using pyZeroConf ZeroConf implimentation..."
		except ImportError, e:
			print e

from metaserver_browser import MetaServerBrowser as RemoteBrowser

if __name__ == '__main__':
	a = LocalBrowser()
	a.run()
