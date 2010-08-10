
from xstruct import pack

from Header import Processed

class Fail(Processed):
	"""\
	The Fail packet consists of:
		* A UInt32, error code
		* A String, may contain useful information for debugging purposes
	"""
	no = 1
	struct = "IS[II]"
	
	reasons = {
		0 : "Protocol Error",
		1 : "Frame Error",
		2 : "Unavailable Permanently",
		3 : "Unavailable Temporarily",
		4 : "No such thing",
		5 : "Permission Denied",
	}
	
	def __init__(self, sequence, errno, s="", references=[]):
		if errno != 0 and sequence < 1:
			raise ValueError("Fail is a reply packet so needs a valid sequence number (%i)" % sequence)
		Processed.__init__(self, sequence)

		self.errno = errno
		self.s = s
		self.references = references
	
	def pack(self):
		output = Processed.pack(self)
		output += pack(self.struct, self.errno, self.s, self.references)

		return output

	def reason(self):
		if self.reasons.has_key(self.errno):
			return self.reasons[self.errno]
		return "Unknown"
	reason = property(reason, doc="A text string representation of the errno")

