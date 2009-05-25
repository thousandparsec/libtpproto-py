
from xstruct import pack

from Header import Processed

class TimeRemaining(Processed):
	"""\
	The TimeRemaining packet consists of:
		* UInt32, Seconds left till the turn ends.
		* 32 bit unsigned enumeration, Reason (why frame was sent):
		    * 0x0 - This frame was requested.
		    * 0x1 - Turn timer has been started
		    * 0x2 - Advanced warning of the turn timer expiring.
		    * 0x3 - All players have finished and the turn has ended.
		    * 0x4 - Threshold of players have finished, the timer for the remaining players has started.
		    * 0x5 - End of turn started.
		* UInt32, Current turn.
		* string, Turn name (may be empty).
	"""
	no = 15
	struct = "jIIS"

	def __init__(self, sequence, time, reason, turn_num, turn_name):
		Processed.__init__(self, sequence)

		# Length is:
		#  * 4 bytes UInt32
		#  * 4 bytes UInt32
		#  * 4 bytes UInt32
		#  * length of string
		#  
		self.length = 4 + \
						4 + \
						4 + \
						4 + len(turn_name)
		self.time = time
		self.reason = reason	
		self.turn_num = turn_num;
		self.turn_name = turn_name;

	def __str__(self):
		output = Processed.__str__(self)
		output += pack(self.struct, self.time, self.reason, self.turn_num, self.turn_name)

		return output
