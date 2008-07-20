
import sys
from os import path
sys.path.insert(0, path.dirname(__file__))

from version import version as vi
from version import installpath as ip
__version__     = vi
__installpath__ = ip

from client import ClientConnection, failed
from adminclient import AdminClientConnection
from server import Server, ServerConnection
Connection = ClientConnection
AdminConnection = AdminClientConnection

Server = Server
ServerConnection = ServerConnection

import objects
from objects import constants

import GenericRS
sys.path.pop(0)
