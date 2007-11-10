
import avahi_disabled

import os, sys
import traceback
import time

import avahi, avahi.ServiceTypeDatabase

import gobject 
import dbus
from dbus.mainloop.glib import DBusGMainLoop

service_type_browsers = {}
service_browsers = {}
service_type_db = avahi.ServiceTypeDatabase.ServiceTypeDatabase()
service_seen = {}

from browse import ZeroConfBrowser as ZeroConfBrowserBase

import threading

class ZeroConfBrowser(ZeroConfBrowserBase):
	def check():
		bus = dbus.SystemBus(mainloop=DBusGMainLoop(set_as_default=False))
		try:
			server = dbus.Interface(bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER), avahi.DBUS_INTERFACE_SERVER)
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
	def callback(self, function):
		def wrapper(*args, **kw):
			self.pending.append((function, args, kw))
		return wrapper

	def service_resolved(self, interface, protocol, name, stype, domain, host, aprotocol, address, port, txt, flags):
		"""\
		Called when all the information about a service is avaliable.
		"""
		assert threading.currentThread() == self.dbusthread

		if len(txt) != 0:
			details = self.pair_to_dict(avahi.txt_array_to_string_array(txt))
		else:
			details = []
		
		self.ServiceFound(name, stype.split('.')[0][1:], (host, address, port), details, details)

	def new_service(self, interface, protocol, name, stype, domain, flags):
		"""\
		Called when a new service is found.
		"""
		assert threading.currentThread() == self.dbusthread

		self.server.ResolveService( interface, protocol, name, stype, domain, \
			avahi.PROTO_UNSPEC, dbus.UInt32(0), reply_handler=self.callback(self.service_resolved), error_handler=self.callback(self.print_error))

	def remove_service(self, interface, protocol, name, stype, domain, flags):
		"""\
		Called when a service disappears.
		"""
		assert threading.currentThread() == self.dbusthread

		self.ServiceGone(name, stype.split('.')[0][1:], None)

	def new_domain(self, interface, protocol, domain, flags):
		"""\
		Called when a new domain appears.
		"""
		assert threading.currentThread() == self.dbusthread

		ifn = self.get_interface_name(interface, protocol)
		if domain != "local":
			self.browse_domain(interface, protocol, domain)

	def browse_domain(self, interface, protocol, domain):
		"""
		Register to browse a given domain.
		"""
		assert threading.currentThread() == self.dbusthread

		# FIXME: This is probably quite bad!
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

		for stype in ['_tp', '_tps', '_tp-http', '_tp-https']:
			stype = stype+'._tcp'
			b = dbus.Interface( \
					self.bus.get_object(avahi.DBUS_NAME, \
						self.server.ServiceBrowserNew(interface, protocol, stype, domain, dbus.UInt32(0))
					), avahi.DBUS_INTERFACE_SERVICE_BROWSER)
			service_browsers[(interface, protocol, stype, domain)] = b
			b.connect_to_signal('ItemNew', self.callback(self.new_service))
			b.connect_to_signal('ItemRemove', self.callback(self.remove_service))

	def __init__(self):
		ZeroConfBrowserBase.__init__(self)

		import dbus.mainloop.glib
		dbus.mainloop.glib.threads_init()

		self.pending = []

	def run(self):
		self.dbusthread = threading.currentThread()

		from dbus.mainloop.glib import DBusGMainLoop
		mainloop = DBusGMainLoop(set_as_default=True)
		self.bus = dbus.SystemBus(mainloop=mainloop)

		self.server   = dbus.Interface(self.bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER), avahi.DBUS_INTERFACE_SERVER)

		# Explicitly browse .local
		self.browse_domain(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, "local")

		# Browse for other browsable domains
		db = dbus.Interface(self.bus.get_object(avahi.DBUS_NAME, self.server.DomainBrowserNew(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, "", avahi.DOMAIN_BROWSER_BROWSE, dbus.UInt32(0))), avahi.DBUS_INTERFACE_DOMAIN_BROWSER)
		db.connect_to_signal('ItemNew', self.new_domain)

		self.mainloop = gobject.MainLoop()
		gcontext = self.mainloop.get_context()
		while not self.mainloop is None:
			if len(self.pending) > 0:
				command, args, kw = self.pending.pop(0)
				command(*args, **kw)

			if gcontext.pending():
				gcontext.iteration()
			else:
				time.sleep(0.01)

	def exit(self):
		if hasattr(self, 'mainloop'):
			self.mainloop.quit()
			self.mainloop = None

def main():
	a = ZeroConfBrowser()
	a.run()

if __name__ == "__main__":
	main()

