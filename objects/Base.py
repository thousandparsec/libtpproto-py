
from xstruct import pack

from Header import Processed

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

		# Length is:
		#  * 4 bytes (uint32 - id)
		#
		self.length = 4 + 4 * len(ids)

		self.ids = ids
	
	def __repr__(self):
		output = Processed.__repr__(self)
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

		# Length is:
		#  * 4 bytes (uint32 - id)
		#
		self.length = 4 + 4 + 4 * len(slots)
	
		self.id = id
		self.slots = slots
	
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.id, self.slots)

		return output

class GetIDSequence(Processed):
	"""\
	Get ID Sequence frame consist of:
		* a SInt32, the sequence key
		* a UInt32, the starting number in the sequence
		* a UInt32, the number of IDs to get

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
	struct = "jII"

	def __init__(self, sequence, key, start, length):
		Processed.__init__(self, sequence)

		self.length = 4 + 4 + 4
	
		self.key = key
		self.start = start
		self.length = length
	
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.key, self.start, self.length)

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
	struct = "jj[IQ]"

	def __init__(self, sequence, key, left, ids):
		Processed.__init__(self, sequence)

		self.length = 4 + 4 + 4 + (4+8) * len(ids)
	
		self.key = key
		self.left = left
		self.ids = ids
	
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.key, self.left, self.ids)

		return output

