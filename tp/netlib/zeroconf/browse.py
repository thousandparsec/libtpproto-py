
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
		print "remove", type, addr
		print self.locations
		if self.locations.has_key(type):
			if addr is None:
				del self.locations[type]
			elif addr in self.locations[type]:
				self.locations[type].remove(addr)

				if len(self.locations[type]) == 0:
					del self.locations[type]

		return len(self.locations) == 0

	def updateOptional(self, optional):
		self.optional.update(optional)

	def updateRequired(self, required):
		self.required.update(required)

	def __getattr__(self, key):
		if hasattr(self, key):
			return self.__dict__[key]
		if self.required.has_key(key):
			return self.required[key]
		if self.optional.has_key(key):
			return self.optional[key]
		raise AttributeError("No such attribute %s" % key)


class ZeroConfBrowser(object):
	def __init__(self):
		self.games = {}

	def ServiceFound(self, name, type, addr, required, optional):
		"""\
		ServiceFound(name, type, addr, tpproto, required, optional)

		type in ['tp', 'tps', 'tphttp', 'tphttps']
		addr is (dns, ip, port)
		
		Required Parameters:
		tp,			is a list of version strings
		server,		version of the server
		servtype,	server type (tpserver-cpp, tpserver-py)
		rule,		ruleset name (MiniSec, TPSec, MyCustomRuleset)
		rulever,	version of the ruleset

		Optional parameters:
		plys,		number of players in the game
		cons,		number of clients currently connected
		objs,		number of "objects" in the game universe
		admin,		admin email address
		cmt,		comment about the game
		turn,		unixtime stamp (GMT) when next turn is generated

		Called when a new server is found.
		"""
		required_keys = ['tp', 'server', 'sertype', 'rule', 'rulever']
		for r in required_keys:
			if not r in required:
				print TypeError("Required parameter %s not found!" % r)

		if not self.games.has_key(name):
			self.games[name] = Game(name)
		else:
			self.games[name].new = False

		game = self.games[name]
		game.addLocation(type, addr)

		game.updateRequired(required)
		game.updateOptional(optional)

		if game.new:
			self.GameFound(game)
		else:
			self.GameUpdate(game)

	def ServiceGone(self, name, type, addr):
		"""\
		Called when a server goes away.

		GameGone(name, type, addr)

		type in ['tp', 'tps', 'tphttp', 'tphttps']
		addr is (dns, ip, port)
		"""

		if not self.games.has_key(name):
			# FIXME: Should print error
			return

		if self.games[name].removeLocation(type, addr):
			game = self.games[name]
			del self.games[name]
			self.GameGone(game)

	def GameFound(self, game):
		print "Found new game", game

	def GameUpdate(self, game):
		print "Updated old game", game

	def GameGone(self, game):
		print "Game disappeared", game

