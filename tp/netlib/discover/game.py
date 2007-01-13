
class Game(object):
	def __init__(self, name):
		self.name = name

		self.locations = {}
		self.required = {}
		self.optional = {}

		self.new = True

	def __str__(self):
		s = "<Game '%s' \n" % self.name
		for type in self.locations.keys():
			s+= "\t%s\t@ " % type
			for addr in self.locations[type]:
				s+= "%s (%s) p %s, " % addr
			s = s[:-2] + "\n"
		s = s[:-1] + ">"
		return s
	__repr__ = __str__

	def addLocation(self, type, addr):
		if not self.locations.has_key(type):
			self.locations[type] = []
		if not addr in self.locations[type]:
			self.locations[type].append(addr)

	def removeLocation(self, type, addr=None):
		"""\
		Removes a location (type, addr) from this game.

		Returns true is that was the last location.
		"""
		if self.locations.has_key(type):
			if addr is None:
				del self.locations[type]
			elif addr in self.locations[type]:
				self.locations[type].remove(addr)

				if len(self.locations[type]) == 0:
					del self.locations[type]

		return len(self.locations) == 0

	preference = ("tps", "tp", "tphttps", "tphttp")
	def bestLocation(self):
		for type in self.preference:
			if self.locations.has_key(type):
				return (type, self.locations[type][0])
		return None

	def updateOptional(self, optional):
		self.optional.update(optional)

	def updateRequired(self, required):
		self.required.update(required)

	def __getattr__(self, key):
		if key in self.__dict__:
			return self.__dict__[key]
		if self.required.has_key(key):
			return self.required[key]
		if self.optional.has_key(key):
			return self.optional[key]
		raise AttributeError("No such attribute %s" % key)
