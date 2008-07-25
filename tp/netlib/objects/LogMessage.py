
from xstruct import pack

from Header import Processed

class LogMessage(Processed):
	"""\
	The LogMessage packet consists of:
		* UInt64, Timestamp (when the message was generated).
		* UInt32, Severity level of the message.
		* String, Message.
	"""
	no = 1000
	struct = "TIS"

	def __init__(self, sequence, timestamp, severity, message):
		Processed.__init__(self, sequence)

		# Length is:
		#
		self.length = 4 + 8 + \
				4 + len(message)

		self.timestamp = timestamp
		self.severity = severity
		self.message = message
	
	def __str__(self):
		output = Processed.__str__(self)
		output += pack(self.struct, self.timestamp, self.severity, self.message)

		return output
