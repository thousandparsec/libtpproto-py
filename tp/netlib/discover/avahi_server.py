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

from server import ZeroConfServer as ZeroConfServerBase
from threading import Thread

class ZeroConfServer(ZeroConfServerBase):
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

	def __init__(self):
		ZeroConfServerBase.__init__(self)

		self.groups = {}
		self.topublish = {}

		bus = dbus.SystemBus()
		self.server = dbus.Interface(bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER), avahi.DBUS_INTERFACE_SERVER)

	def ServiceRemove(self, name, type, addr):
		print "ServiceRemove"
		key = (name, type, addr)
		if key in self.groups:
			group = self.groups[key]
			del self.groups[key]
			group.Reset()

	def ServiceAdd(self, name, type, addr, required, optional):
		print "ServiceAdd"

		stype = "_%s._tcp" % type

		entrygroup = self.server.EntryGroupNew()
		group = dbus.Interface(dbus.SystemBus().get_object(avahi.DBUS_NAME, entrygroup), avahi.DBUS_INTERFACE_ENTRY_GROUP)

		def entry_group_state_changed(state, hrm, self=self, entrygroup=entrygroup):
			print "entry_group_state_changed...."
			print state, hrm, self, entrygroup
			group = dbus.Interface(dbus.SystemBus().get_object(avahi.DBUS_NAME, self.server.EntryGroupNew()), avahi.DBUS_INTERFACE_ENTRY_GROUP)
			self.entry_group_state_changed(group, state)
		group.connect_to_signal('StateChanged', entry_group_state_changed)

		print "Adding service '%s' of type '%s' ..." % (name, stype)
		txt = self.dict_to_pair(required) + self.dict_to_pair(optional)
		print txt, addr, avahi.string_array_to_txt_array(txt)
		group.AddService(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, 0,
			name, stype, "", "", dbus.UInt16(addr[2]), 
			avahi.string_array_to_txt_array(txt))
		group.Commit()

		self.groups[(name, type, addr)] = group

	def entry_group_state_changed(self, group, state):
		print "entry_group_state_changed..."
		if state == avahi.ENTRY_GROUP_ESTABLISHED:
			print group, "Service established."
		elif state == avahi.ENTRY_GROUP_COLLISION:
			n_rename = n_rename + 1
			if n_rename >= 12:
				print "ERROR: No suitable service name found after %i retries, exiting." % n_rename
			else:
				name = self.server.GetAlternativeServiceName(name)
				print "WARNING: Service name collision, changing name to '%s' ..." % name

	def dict_to_pair(self, l):
		res = []
		for key, value in l.items():
			if len(value) < 1:
				res.append(key)
			else:
				res.append("%s=%s" % (key, value))
		return res

	######################################
	# Callback functions
	######################################

	def run(self):
		print "avahi_browse", self

		self.mainloop = gobject.MainLoop()
		gcontext = self.mainloop.get_context()

		bus = dbus.SystemBus()
		while not self.mainloop is None:
			if gcontext.pending():
				gcontext.iteration()
			else:
				time.sleep(0.01)

	def exit(self):
		self.mainloop.quit()
		self.mainloop = None

def main():
	from game import Game

	game1 = Game("testing 1")
	game1.updateRequired({'tp': '0.3', 'server': 'None', 'sertype':'Avahi Testing Script', 'rule': "Testing Avahi!", 'rulever': 'None'})
	game1.addLocation("tp", ("mithro.local", "10.1.1.1", 80))

	game2 = Game("testing 2")
	game2.updateRequired({'tp': '0.3', 'server': 'None', 'sertype':'Avahi Testing Script', 'rule': "Testing Avahi!", 'rulever': 'None'})
	game2.addLocation("tp",  ("mithro.local", "10.1.1.1", 8080))
#	game2.addLocation("tp",  ("mithro.local", "10.1.1.1", 443)) -- Can't have to services on the same name and type
	game2.addLocation("tps", ("mithro.local", "10.1.1.1", 90))

	a = ZeroConfServer()
	a.GameAdd(game1)
	a.GameAdd(game2)
	a.run()

if __name__ == "__main__":
	main()

