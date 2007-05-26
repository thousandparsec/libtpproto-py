
class ZeroConfServer(object):
	def __init__(self):
		self.games = {}

	def GameAdd(self, game):
		"""\
		Add a new game to be advitised by ZeroConf. All the locations
		will be advertised.
		"""
		required_keys = ['tp', 'server', 'sertype', 'rule', 'rulever']
#		for r in required_keys:
#			if not r in game.required:
#				print TypeError("Required parameter %s not found!" % r)

		if self.games.has_key(game.name):
			raise SyntaxException("Game with that name already exists!")
		
		self.games[game.name] = game
		
		for type in game.locations.keys():
			for location in game.locations[type]:
				self.ServiceAdd(game.name, type, location, game.required, game.optional)

	def GameUpdate(self, game):
		"""\
		Update a game which is already advertised by ZeroConf.
		"""
		if not self.games.has_key(game.name):
			raise SyntaxException("Game with that name does not exist!")
	
		# Remove the old details	
		self.GameRemove(self.games[game.name])
		# Add the new details
		self.GameAdd(game)

	def GameRemove(self, game):
		"""\
		Remove a game which is being advertised by ZeroConf.
		"""
		if not self.games.has_key(game.name):
			raise SyntaxException("Game with that name does not exist!")

		oldgame = self.games[game.name]
		for type in game.locations.keys():
			for location in game.locations[type]:
				self.ServiceRemove(game.name, type, location)
		del self.games[game.name]

	def ServiceRemove(self, name, type, addr):
		"""\
		ServiceRemove(name, type, addr, tpproto, required, optional)

		type in ['tp', 'tps', 'tp+http', 'tp+https']
		addr is (dns, ip, port)
		
		Called to remove an old service.
		"""
		print "ServiceAdd", self, name, type, addr

	def ServiceAdd(self, name, type, addr, required, optional):
		"""\
		ServiceAdd(name, type, addr, tpproto, required, optional)

		type in ['tp', 'tps', 'tp+http', 'tp+https']
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

		Called to add a new service.
		"""
		print "ServiceAdd", self, name, type, addr, required, optional
