
from xstruct import pack

from Header import Processed

class Game(Processed):
	"""\
	 A Game Description frame consist of:
		* a String, Game name
		* a String, Key
		* a list of Strings, List of protocol versions supported
		* a String, Server Version
		* a String, Server Type
		* a String, Ruleset Name
		* a String, Ruleset Version
		* a list of,
			* a String, Connection Type
			* a String, Resolvable DNS name
			* a String, IP Address
			* a UInt32, Port
		* a list of,
			* a UInt32, Optional Paramater ID
			* a String, String Value
			* a UInt32, Int Value
        * Media base URI
	"""
	no = 66
	struct = "SS[S]SSSS[SSSI][ISI]ST"
	options = {
		1: ("plys", "players", "Number of Players in the game."),
		2: ("cons",	"connected", "Number of Clients currently connected."),
		3: ("objs", "objects", "Number of objects in the game universe."),
		4: ("admin", "admin", "Admin email address."),
		5: ("cmt", "comment", "Comment about the game."),
		6: ("turn", "turn", "When the next turn is generated."),
	}

	def __init__(self, sequence, name, key, \
			tp, server, sertype, rule, rulever, \
			locations, optional, media, ctime):
		Processed.__init__(self, sequence)

		self.name    = name
		self.key     = key
		self.tp      = tp
		self.server  = server
		self.sertype = sertype
		self.rule    = rule
		self.rulever = rulever
		self.locations = locations
		self._optional = optional
		self.media   = media
		self.ctime   = ctime

	def _optional_set(self, optional):
		for option in optional:
			if option[0] in Game.options:
				value = option[1]
				if len(value) == 0:
					value = option[2]
				setattr(self, Game.options[option[0]][0], value)

	def _optional_get(self):
		optional = []
		for key, (short, long, comment) in Game.options.items():
			if hasattr(self, short):
				value = getattr(self, short)
				if isinstance(value, (str, unicode)):
					optional.append((key, value, 0))
				else:
					optional.append((key, "", value))
		return optional
	_optional = property(_optional_get, _optional_set)

	def optional_get(self):
		optional = {}
		for key, (short, long, comment) in Game.options.items():
			if hasattr(self, short):
				optional[short] = getattr(self, short)
		return optional
	optional = property(optional_get)

	def required_get(self):
		required = {}
		for i in ['tp', 'server', 'sertype', 'rule', 'rulever']:
			required[i] = getattr(self, i)
		return required
	required = property(required_get)

	def pack(self):
		output = Processed.pack(self)
		output += pack(self.struct, 
			self.name, \
			self.key,
			self.tp, \
			self.server, self.sertype, \
			self.rule, self.rulever, \
			self.locations, \
			self._optional, \
			self.media, \
			self.ctime)
		return output
