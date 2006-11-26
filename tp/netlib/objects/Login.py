
from xstruct import pack

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

		# Length is:
		#  * 4 bytes (uint32 - string length)
		#  * the string
		#  * null terminator
		#  * 4 bytes (uint32 - string length)
		#  * the string
		#  * null terminator
		#
		self.length = 4 + len(username) + 4 + len(password)

		self.username = username
		self.password = password
	
	def __str__(self):
		output = Processed.__str__(self)
		output += pack(self.struct, self.username, self.password)

		return output
