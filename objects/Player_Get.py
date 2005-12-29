from Base import GetWithID

class Player_Get(GetWithID):
	"""\
	The Player_Get packet consists of:
		* A list of uint32, IDs of players to get.
	
	A player ID of 0 is the current player.
	"""
	no = 39

