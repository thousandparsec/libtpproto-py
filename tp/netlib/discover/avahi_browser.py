import os, sys
import traceback
import time

import avahi, avahi.ServiceTypeDatabase

import gobject 
import dbus
if getattr(dbus, 'version', (0,0,0)) >= (0,41,0):
    import dbus.glib

service_type_browsers = {}
service_browsers = {}
service_type_db = avahi.ServiceTypeDatabase.ServiceTypeDatabase()
service_seen = {}

from browse import ZeroConfBrowser as ZeroConfBrowserBase

class ZeroConfBrowser(ZeroConfBrowserBase):
	def check():
		bus = dbus.SystemBus()
		server = dbus.Interface(bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER), avahi.DBUS_INTERFACE_SERVER)
		try:
			print "avahi version", server.GetVersionString()
		except dbus.DBusException, e:
			print e
			return False
		return True
	check = staticmethod(check)

	######################################
	# Helper functions
	######################################
	def protoname(self, protocol):
		if protocol == avahi.PROTO_INET:
			return "IPv4"
		if protocol == avahi.PROTO_INET6:
			return "IPv6"
		return "n/a"

	def siocgifname(self, interface):
		if interface <= 0:
			return "n/a"
		else:
			return self.server.GetNetworkInterfaceNameByIndex(interface)

	def get_interface_name(self, interface, protocol):
		if interface == avahi.IF_UNSPEC and protocol == avahi.PROTO_UNSPEC:
			return "Wide Area"
		else:
			return str(self.siocgifname(interface)) + " " + str(self.protoname(protocol))

	def lookup_type(self, stype):
		global service_type_db
		try:
			return service_type_db[stype]
		except KeyError:
			return stype

	def print_error(self, err):
		print "Error:", str(err)

	def pair_to_dict(self, l):
		res = dict()
		for el in l:
			if "=" not in el:
				res[el]=''
			else:
				tmp = el.split('=',1)
				if len(tmp[0]) > 0:
					res[tmp[0]] = tmp[1]
		return res

	######################################
	# Callback functions
	######################################
	def service_resolved(self, interface, protocol, name, stype, domain, host, aprotocol, address, port, txt, flags):
		"""\
		Called when all the information about a service is avaliable.
		"""
		if len(txt) != 0:
			details = self.pair_to_dict(avahi.txt_array_to_string_array(txt))
		else:
			details = []
		
		self.ServiceFound(name, stype.split('.')[0][1:], (host, address, port), details, details)

	def new_service(self, interface, protocol, name, stype, domain, flags):
		"""\
		Called when a new service is found.
		"""
		self.server.ResolveService( interface, protocol, name, stype, domain, \
			avahi.PROTO_UNSPEC, dbus.UInt32(0), reply_handler=self.service_resolved, error_handler=self.print_error)

	def remove_service(self, interface, protocol, name, stype, domain, flags):
		"""\
		Called when a service disappears.
		"""
		self.ServiceGone(name, stype.split('.')[0][1:], None)

	def new_domain(self, interface, protocol, domain, flags):
		"""\
		Called when a new domain appears.
		"""
		print self, interface, protocol, domain, flags
		ifn = self.get_interface_name(interface, protocol)
		if domain != "local":
			self.browse_domain(interface, protocol, domain)

	def browse_domain(self, interface, protocol, domain):
		"""
		Register to browse a given domain.
		"""
		global service_type_browsers

		# Are we already browsing this domain?
		if service_type_browsers.has_key((interface, protocol, domain)):
			return

		try:
			b = dbus.Interface( \
					self.bus.get_object(avahi.DBUS_NAME, \
						self.server.ServiceTypeBrowserNew(interface, protocol, domain, dbus.UInt32(0))
					),  avahi.DBUS_INTERFACE_SERVICE_TYPE_BROWSER)
		except dbus.DBusException, e:
			print e
			traceback.print_exc()

		for stype in ['_tp', '_tps', '_tphttp', '_tphttps']:
			stype = stype+'._tcp'
			b = dbus.Interface( \
					self.bus.get_object(avahi.DBUS_NAME, \
						self.server.ServiceBrowserNew(interface, protocol, stype, domain, dbus.UInt32(0))
					), avahi.DBUS_INTERFACE_SERVICE_BROWSER)
			b.connect_to_signal('ItemNew', self.new_service)
			b.connect_to_signal('ItemRemove', self.remove_service)
			service_browsers[(interface, protocol, stype, domain)] = b

	def __init__(self):
		ZeroConfBrowserBase.__init__(self)

		self.bus = dbus.SystemBus()
		self.server = dbus.Interface(self.bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER), avahi.DBUS_INTERFACE_SERVER)

	def run(self):
		print "avahi_browse", self

		# Explicitly browse .local
		self.browse_domain(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, "local")

		# Browse for other browsable domains
		db = dbus.Interface(self.bus.get_object(avahi.DBUS_NAME, self.server.DomainBrowserNew(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, "", avahi.DOMAIN_BROWSER_BROWSE, dbus.UInt32(0))), avahi.DBUS_INTERFACE_DOMAIN_BROWSER)
		db.connect_to_signal('ItemNew', self.new_domain)

		self.mainloop = gobject.MainLoop()
		gcontext = self.mainloop.get_context()
		while not self.mainloop is None:
			if gcontext.pending():
				gcontext.iteration()
			else:
				time.sleep(0.01)
			

	def exit(self):
		self.mainloop.quit()
		self.mainloop = None

def main():
	a = ZeroConfBrowser()
	a.run()

if __name__ == "__main__":
	main()

