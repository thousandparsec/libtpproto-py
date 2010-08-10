
from xstruct import pack

from Header import Processed

class Account(Processed):
	"""\
	The Account packet consists of:
		* A String, a requested username
		* A String, the password
		* A String, the email address
		* A String, a comment

		FIXME: * A String, the game (some servers may support multiple games on one server)
	"""
	no = 62
	struct = "SSSS"

	def __init__(self, sequence, username, password, email, comment):
		Processed.__init__(self, sequence)

		self.username = username
		self.password = password
		self.email    = email
		self.comment  = comment
	
	def pack(self):
		output = Processed.pack(self)
		output += pack(self.struct, self.username, self.password, self.email, self.comment)

		return output
