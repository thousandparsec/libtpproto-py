from Get import Get

class Board_Get(Get):
	"""\
	The Board_Get packet consists of:
		* A list of uint32, IDs of message boards to get.
	"""
	no = 16

