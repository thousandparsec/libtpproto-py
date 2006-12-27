
try:
	from avahi_browser import ZeroConfBrowser as Browser
	if not Browser.check():
		raise ImportError("Can't use avahi as it isn't running!")
	print "Using avahi ZeroConf implimentation..."
except ImportError, e:
	print e
	try:
		from bonjour_browser import ZeroConfBrowser as Browser
		print "Using bonjour ZeroConf implimentation..."
	except ImportError, e:
		print e
		try:
			from pyzeroconf_browser import ZeroConfBrowser as Browser
			print "Using pyZeroConf ZeroConf implimentation..."
		except ImportError, e:
			print e

if __name__ == '__main__':
	a = Browser()
	a.run()
