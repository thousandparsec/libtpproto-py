
import time
import urllib

from browse import Browser, Game
metaserver = "http://metaserver.thousandparsec.net/"

def getpacket(data):
	header, data = data[:objects.Header.size], data[objects.Header.size:]
	p = objects.Header(header)
	p.process(data[:p.length])

 	return p, data[p.length:]

from tp.netlib import objects

class MetaServerBrowser(Browser):
	def __init__(self, timeout=60*10):
		self.timeout = timeout
		self.waittill = 0
		self.games = {}

		self._exit = False

	def exit(self):
		self._exit = True

	def run(self):
		print "metaserver_browse", self

		while not self._exit:
			now = time.time()
			print self.waittill, now
			if self.waittill < now:
				data = urllib.urlopen(metaserver, urllib.urlencode({'action': 'get'})).read()
				if data[:4] == "TP03":

					p, data = getpacket(data)
					if isinstance(p, objects.Fail):
						print p.error
					elif isinstance(p, objects.Sequence):
						g = self.games
						for game in g.values():
							game.notfound = True

						for i in range(0, p.number):
							p, data = getpacket(data)

							if not isinstance(p, objects.Game):
								raise TypeError("The metaserver returned an incorrect response (expected Game packet)...")

							if not p.name in g:
								game = Game(p.name)
							else:
								game = g[p.name]
								
							game.updateOptional(p.optional)
							game.updateRequired(p.required)

							game.locations = {}
							for type, dns, ip, port in p.locations:
								game.addLocation(type, (dns, ip, port))

							if game.new:
								self.GameFound(game)
								game.new = False
							else:
								self.GameUpdate(game)

							game.notfound = False
					
							g[game.name] = game
	
						for k, game in g.items():
							if game.notfound:
								del g[k]
								self.GameGone(game)
					else:
						raise TypeError("The metaserver returned an incorrect response (expected Failure or Sequence)...") 

				self.waittill = now + self.timeout
			time.sleep(min(1, self.waittill - time.time()))

def main():
	a = MetaServerBrowser()
	a.run()

if __name__ == "__main__":
	main()

