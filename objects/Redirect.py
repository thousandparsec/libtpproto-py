
from xstruct import pack

from Header import Processed

class Redirect(Processed):
	"""\
	 Redirect frame consist of:
		* a String, the URI of the new server to connect too

	This URI will be of the standard format. A server won't redirect to a 
	different type of service (IE If you using the tunnel service it will only
	redirect to another tunnel service).

	Example URIs:
		* tp://mithro.dyndns.org/ - Connect on standard tp port
		* tps://mithro.dyndns.org/ - Connect on standard tps port using SSL
		* tp://mithro.dyndns.org:6999/ - Connect on port 6999
		* http://mithro.dyndns.org/ - Connect using http tunneling
		* https://mithro.dyndns.org/ - Connect using https tunneling
	"""

	no = 24
	struct = "S"

	def __init__(self, sequence, s=""):
		Processed.__init__(self, sequence)

		# Length is:
		#  * 4 bytes (uint32 - string length)
		#  * the string
		#  * null terminator
		#
		self.length = 4 + len(s) + 1

		self.s = s
	
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.s)

		return output
