# Python Imports
import select
import socket
import string
import sys

# Local imports
import xstruct
import objects
constants = objects.constants

from common import Connection

class Server:
	address_family = socket.AF_INET
	socket_type = socket.SOCK_STREAM

	def __init__(self, address, port):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.s.bind((address, port))
		self.s.listen(5)

		# We are non blocking
		self.s.setblocking(False)

		self.connections = []
		
	def serve_forever(self):
		while True:
			# Check if there is any socket to accept or with data
			ready, trash, errors = select.select([self.s] + self.connections,[],self.connections,1)

			for socket in ready:
				if socket is self.s:
					# Accept a new connection
					socket, address = self.s.accept()
					self.connections.append(ServerConnection(socket, address, debug=True))
				else:
					socket.poll()
			
			# Cleanup any old socket
			for socket in errors:
				self.connections.remove(socket)
				del socket

class ServerConnection(Connection):
	def __init__(self, socket, address, debug=False):
		self.address = address

		self.setup(socket, debug=debug, nb=True)

	def fileno(self):
		return self.s.fileno()

	def poll(self):
		"""\
		Checks to see if any packets are on the line
		"""
		# Complete any pending commands
		Connection.poll(self)

		# Get the packets
		self._recv(-1)
		
		sequences = self.rbuffer.keys()
		sequences.sort()
		for sequence in sequences:
			packet = self._recv(sequence)

			if not packet:
				continue

			success = False
			for c in [packet.__class__] + list(packet.__class__.__bases__):
				function = "On" + c.__name__
	
				if hasattr(self, function):
					success = getattr(self, function)(packet)
					break
				
			if not success:
				self._send(objects.Fail(packet.sequence, constants.FAIL_PERM, "Service unavalible."))

	def _description_error(self, packet):
		self._send(objects.Fail(packet.sequence, constants.FAIL_FRAME, "Packet which doesn't have a possible description."))

	def OnInit(self):
		pass

	def OnConnect(self, packet):
		self._send(objects.OK(packet.sequence, "Welcome to py-server!"))
		return True

if __name__ == "__main__":
	port = 6924
	while True:
		try:
			s = Server("127.0.0.1", port=port)
		except:
			print "This port in use...", port
			port += 1
			continue
		s.serve_forever()

