
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

		try:
			zeroconf = Zeroconf.Zeroconf("0.0.0.0")
			self.browser = Zeroconf.ServiceBrowser(zeroconf, self.types, self)
		except socket.error, e:
			print "Unable to create pyZeroconf Browser", e
			self.browser = None
	
	def removeService(self, server, type, name):
		name = name[:-len(type)-1]
		self.ServiceGone(name, type.split('.')[0][1:], None)

	def addService(self, server, type, name):
		# Request more information about the service
	
		i = 0
		while i < 15:
			info = server.getServiceInfo(type, name)
			fname = name[:-len(type)-1]

			print name, fname, info.getServer(), dir(info)
			if not info is None:
				self.ServiceFound(fname, type.split('.')[0][1:], \
					(info.getServer()[:-1], str(socket.inet_ntoa(info.getAddress())), info.getPort()), \
					info.getProperties(), info.getProperties())
				break
			print "Unable to get service info for %s (%s) :(" % (name, type)
			i+=1


	def run(self):
		try:
			if self.browser != None:
				self.browser.run()
		except Exception, e:
			print e
			traceback.print_exc()
		globals()['_GLOBAL_DONE'] = True

	def exit(self):
		globals()['_GLOBAL_DONE'] = True

def main():
	a = ZeroConfBrowser()
	a.run()

if __name__ == "__main__":
	main()
