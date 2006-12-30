
import traceback, socket
from pyZeroconf import Zeroconf

from browse import ZeroConfBrowser as ZeroConfBrowserBase

class ZeroConfBrowser(ZeroConfBrowserBase):
	def __init__(self):
		ZeroConfBrowserBase.__init__(self)

		types = []
		for stype in ['_tp', '_tps', '_tphttp', '_tphttps']:
			types.append(stype+'._tcp.local.')
		self.types = types		

		zeroconf = Zeroconf.Zeroconf("0.0.0.0")
		self.browser = Zeroconf.ServiceBrowser(zeroconf, self.types, self)
	
	def exit(self):
		globals()['_GLOBAL_DONE'] = True

	def removeService(self, server, type, name):
		name = name[:-len(type)-1]
		self.ServiceGone(name, type.split('.')[0][1:], None)

	def addService(self, server, type, name):
		# Request more information about the service
		info = server.getServiceInfo(type, name)
		name = name[:-len(type)-1]
		if not info is None:
			self.ServiceFound(name, type.split('.')[0][1:], \
				(info.getServer()[:-1], str(socket.inet_ntoa(info.getAddress())), info.getPort()), \
				info.getProperties(), info.getProperties())
		else:
			print "Unable to get service info for %s (%s) :(" % (name, type)

	def run(self):
		try:
			self.browser.run()
		except Exception, e:
			print e
			traceback.print_exc()
			globals()['_GLOBAL_DONE'] = True

def main():
	a = ZeroConfBrowser()
	a.run()

if __name__ == "__main__":
	main()
