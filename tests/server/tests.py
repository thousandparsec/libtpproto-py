
import objects
from connection import Connection

def test1(host, port):
	"""\
	Testing connecting and disconnecting without sending any data.
	"""
	try:
		c = Connection("127.0.0.1")
		c.disconnect()

		return True, None
	except Exception, e: 
		return False, e

def test2(host, port):
	"""\
	Testing connecting and sending junk.
	"""
	try:
		c = Connection("127.0.0.1")
		c._send("Junk!")

		# Should return a fail packet
		p = c._recv()

		if isinstance(p, objects.Fail):
			return True, None
		else:
			return False, "Did not return correct packet type."
		
	except Exception, e:
		return False, e

	
c = Connection("127.0.0.1")
c.connect()



