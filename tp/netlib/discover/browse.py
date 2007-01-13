class Browser(object):
	def GameFound(self, game):
		print "Found new game", game

	def GameUpdate(self, game):
		print "Updated old game", game

	def GameGone(self, game):
		print "Game disappeared", game

from game import Game
class ZeroConfBrowser(Browser):
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

