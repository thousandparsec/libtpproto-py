
from xstruct import pack

from constants import *
from Header import Processed

class Feature(Processed):
	"""\
	The Features frame consists of:
		* a List of UInt32, ID code of feature
	"""
	no = 26
	struct = "[I]"

	possible = {
		FEATURE_SECURE_THIS:		"Secure Connection available on this port",
		FEATURE_SECURE_OTHER:		"Secure Connection available on another port",
		FEATURE_HTTP_THIS:			"HTTP Tunneling available on this port",
		FEATURE_HTTP_OTHER:			"HTTP Tunneling available on another port",
		FEATURE_KEEPALIVE:			"Supports Keep Alive frames",
		FEATURE_ORDERED_OBJECT:		"Sends Object ID Sequences in decending modified time order",
		FEATURE_ORDERED_ORDERDESC:	"Sends Order Description ID Sequences in decending modified time order",
		FEATURE_ORDERED_BOARD:		"Sends Board ID Sequences in decending modified time order",
		FEATURE_ORDERED_RESOURCE:	"Sends Resource Description ID Sequences in decending modified time order",
		FEATURE_ORDERED_CATEGORY:	"Sends Category Description ID Sequences in decending modified time order",
		FEATURE_ORDERED_COMPONENT:	"Sends Component ID Sequences in decending modified time order",

		FEATURE_ACCOUNT_REGISTER:	"Client can register an account through the client",
	}

	def __init__(self, sequence, features):
		Processed.__init__(self, sequence)

		self.features = features
	
	def pack(self):
		output = Processed.pack(self)
		output += pack(self.struct, self.features)

		return output
