
class References(dict):
	def __init__(self, references):
		self.references = references

		self.dirty = True

	def types(self):
		if len(self.references) > 0:
			if self.dirty:
				self.__types = zip(*self.references)[0]
			return self.__types
		return []
	types = property(types)

	def __len__(self):
		return len(self.references)

	def __iter__(self):
		return self.references.__iter__()

	def __str__(self):
		s = "<References\n"
		for type, value in self.references:
			if type > 0:
				s += "\t%s: %s\n" % (Types[type], value)
			else:
				value = globals()[Types[type].replace(" ","")][value]
				s += "\t%s: '%s'\n" % (Types[type], value)
		return s[:-1]+">"
	
	def GetReferenceValue(self, type, value):
		if type <= 0:
			return globals()[Types[type].replace(" ","")][value]
		else:
			return value

class ReferenceDict(dict):
	def __init__(self, dict):

		self.reverse = {}
		for key, value in dict.items():
			self.reverse[value[0]] = key
		self.forward = {}
		for key, value in dict.items():
			self.forward[key] = value[0]

		self.__help = {}
		for key, value in dict.items():
			self.__help[key]		= value[1]
			self.__help[value[0]]	= value[1]

	def help(self, key):
		"""\
		A description of the object.
		"""
		return self.__help[key]

	def __getitem__(self, key):
		if self.forward.has_key(key):
			return self.forward[key]
		elif self.reverse.has_key(key):
			return self.reverse[key]
		raise KeyError("%s doesn't exist in the dictionary.")

	def __setitem__(self, key, value):
		raise RuntimeError("This dictionary is read only")

	def __len__(self):
		return len(self.forward)


Types = ReferenceDict({
	-1000:	("Server Specific", ""),
	-5: ("Design Action", ""),
	-4: ("Player Action", ""),
	-3: ("Message Action", ""),
	-2:	("Order Action", ""),
	-1:	("Object Action", ""),
	0:	("Misc", ""),
	1:	("Object", ""),
	2:	("Order Type", ""),
	3:	("Order Instance", ""),
	4:	("Board", ""),
	5:	("Message", ""),
	6:	("Resource Description", ""),
	7:	("Player", ""),
	8:	("Category", ""),
	9:	("Design", ""),
})

Misc = ReferenceDict({
   1: ("System",		"This message is from a the internal game system."),
   2: ("Administration","This message is an message from game administrators."),
   3: ("Important",		"This message is flagged to be important."),
   4: ("Unimportant",	"This message is flagged as unimportant."),
})
PlayerAction = ReferenceDict({
   1: ("Player Eliminated",	"This message refers to the elimination of a player from the game"),
   2: ("Player Quit",		"This message refers to a player leaving the game"),
   3: ("Player Joined",		"This message refers to a new player joining the game"),
})
OrderAction = ReferenceDict({
   1: ("Order Completion",		"This message refers to a completion of an order."),
   2: ("Order Canceled",		"This message refers to the cancellation of an order."),
   3: ("Order Incompatible",	"This message refers to the inability to complete an order."),
   4: ("Order Invalid",			"This message refers to an order which is invalid."),
})
ObjectAction = ReferenceDict({
   1: ("Object Idle", "this message refers to an object having nothing to do"),
})

if __name__ == "__main__":
	print Misc[1], Misc["System"], Misc.help(1), Misc.help("System")
	print References([(-1, 1), (-2, 3)])
