from Base import GetWithID

class Board_Get(GetWithID):
	"""\
	The Board_Get packet consists of:
		* A list of uint32, IDs of message boards to get.
	"""
	no = 16

