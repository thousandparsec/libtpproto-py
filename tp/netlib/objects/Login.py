
from xstruct import pack

from Header import Header
from Header import Processed

class Login(Processed):
	"""\
	The Login packet consists of:
		* A string, Username to login with.
		* A string, Password for the username.
	"""

	no = 4
	struct = "SS"

	def __init__(self, sequence, username, password):
		Processed.__init__(self, sequence)

		self.username = username
		self.password = password

	def pack(self):
		output = Processed.pack(self)
		output += pack(self.struct, self.username, self.password)

		return output
