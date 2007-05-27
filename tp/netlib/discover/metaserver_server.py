
import time
import urllib

from server import Server, Game
metaserver = "http://metaserver.thousandparsec.net/"
metaserver = "http://localhost/"

class MetaServerServer(Server):
	def __init__(self, timeout=60*10):
		self.timeout = timeout
		self.waittill = 0
		self.games = {}

		self._exit = False

	def GameAdd(self, game):
		if self.games.has_key(game.name):
			raise SyntaxException("Game with that name already exists!")
		
		self.games[game.name] = game
		
		# Reset the wait time
		self.waittill = time.time()

	def GameRemove(self, game):
		if not self.games.has_key(game.name):
			raise SyntaxException("Game with that name does not exist!")

		oldgame = self.games[game.name]
		for type in game.locations.keys():
			for location in game.locations[type]:
				self.ServiceRemove(game.name, type, location)
		del self.games[game.name]
		self.games.remove(game)


	def exit(self):
		self._exit = True

	def run(self):
		print "metaserver_browse", self

		while not self._exit:
			now = time.time()
			if self.waittill < now:
				for game in self.games.values():
					param = {}
					param['action'] = 'update'
					param['name']   = game.name
					for n, v in game.required.items():
						param[n] = v
					for n, v in game.optional.items():
						param[n] = v

					for type, locations in game.locations.items():
						for i, location in enumerate(locations):
							param['type%i' % i] = type
							param['dns%i'  % i] = location[0]
							param['ip%i'   % i] = location[1]
							param['port%i' % i] = location[2]

					data = urllib.urlopen(metaserver, urllib.urlencode(param)).read()
					print data

				self.waittill = now + self.timeout
			time.sleep(min(60, self.waittill - time.time()))

def main():
	a = MetaServerServer()

	g = Game('testing!')
	g.updateRequired({'key': 'abc', 'tp': '0.3', 'server': 'bazillion!', 'sertype': 'none!', 'rule':'Testing', 'rulever': '0.0.1'})
	g.updateOptional({'admin': 'abc@peanut!', 'cmt':'Hello!'})
	g.addLocation('tp+http', ('localhost', '127.0.0.1', 6923))

	a.GameAdd(g)

	a.run()

if __name__ == "__main__":
	main()

