
import sys
from os import path
sys.path.insert(0, path.dirname(__file__))

from version import version

from client import ClientConnection, failed
from server import Server, ServerConnection
Connection = ClientConnection

Server = Server
ServerConnection = ServerConnection

import objects
import clang

sys.path.pop(0)
