
from xstruct import pack

from Header import Header, Processed

class GetWithID(Processed):
	"""\
	A Get with ID frame consist of:
		* a list of UInt32, IDs of the things requested
	
	This packet is used to get things using their IDs. Such things would 
	be objects, message boards, etc.
	"""	
	struct = "[j]"

	def __init__(self, sequence, ids):
		Processed.__init__(self, sequence)

		self.ids = ids
	
	def pack(self):
		output = Processed.pack(self)
		output += pack(self.struct, self.ids)

		return output
		
class GetWithIDandSlot(Processed):
	"""\
	Get with ID and Slot frame consist of:
		* a UInt32, id of base thing
		* a list of UInt32, slot numbers of contained things be requested

	This packet is used to get things which are in "slots" on a parent. 
	Examples would be orders (on objects), messages (on boards), etc.

	Note: If this is really a Remove frame then slot numbers should be in 
	decrementing value if you don't want strange things to happen. 
	(IE 10, 4, 1) 	
	"""
	struct = "I[j]"

	def __init__(self, sequence, id, slots):
		Processed.__init__(self, sequence)

		self.id = id
		self.slots = slots
	
	def pack(self):
		output = Processed.pack(self)
		output += pack(self.struct, self.id, self.slots)

		return output

class GetIDSequence(Processed):
	"""\
	Get ID Sequence frame consist of:
		* a SInt32, the sequence key
		* a UInt32, the starting number in the sequence
		* a SInt32, the number of IDs to get
		* a timestamp, only IDs which have a modification time greater then this time

	Requirements:
		* To start a sequence, the key of -1 should be sent in the first
		  request
		* Subsequent requests in a sequence should use the key which is 
		  returned
		* All requests must be continuous and ascending
		* Only one sequence key can exist at any time, starting a new 
		  sequence causes the old one to be discarded
		* Key persist for only as long as the connection remains and there
		  are IDs left in the sequence
	"""
	struct = "jIjp"

	def __init__(self, sequence, key, start, amount, since=-1):
		Processed.__init__(self, sequence)

		self.key    = key
		self.start  = start
		self.amount = amount
		self.since  = since
	
	def pack(self):
		output = Processed.pack(self)
		output += pack(self.struct, self.key, self.start, self.amount, self.since)

		#assert len(output) == Header.size+self.length, "Output length (%s) did not match out length! (%s)" % (len(output, self.length))

		return output

class IDSequence(Processed):
	"""\
	ID Sequence frame consist of:
		* a SInt32, the sequence key
		* a SInt32, the number of IDs remaining
		* a list of
			* a UInt32, the IDs
			* a UInt64, the last modified time of this ID

	These IDs are not guaranteed to be in any order. 	
	"""
	struct = "jj[IT]p"

	def __init__(self, sequence, key, left, ids, since=0):
		Processed.__init__(self, sequence)

		self.key   = key
		self.left  = left
		self.ids   = ids
		self.since = since
	
	def pack(self):
		output = Processed.pack(self)
		output += pack(self.struct, self.key, self.left, self.ids, self.since)

		return output

