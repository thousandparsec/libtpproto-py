
version = (0, 0, 5)

import sys
from os import path
sys.path.insert(0, path.dirname(__file__))

from client import ClientConnection
from server import Server, ServerConnection
Connection = ClientConnection

Server = Server
ServerConnection = ServerConnection

import types
import objects
def failed(object):
	if type(object) == types.TupleType:
		return not object[0]
	else:
		if isinstance(object, objects.Fail):
			return True
	return False

