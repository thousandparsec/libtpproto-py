# Python Imports
import select
import socket
import sys
import traceback

# Local imports
import objects
constants = objects.constants

from common import Connection

class ServerConnection(Connection):
	def __init__(self, socket, address, debug=False):
		Connection.__init__(self)

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
		
		sequences = self.buffers['receive'].keys()
		sequences.sort()
		for sequence in sequences:
			p = self._recv(sequence)

			if not p:
				continue

			success = False

			bases = [p.__class__]
			while len(bases) > 0:
				print bases

				c = bases.pop(0)
				function = "On" + c.__name__
				print function
	
				if hasattr(self, function):
					try:
						success = getattr(self, function)(p)
					except:
						type, val, tb = sys.exc_info()
						print ''.join(traceback.format_exception(type, val, tb))
					break
				
				bases += list(c.__bases__)

			if not success:
				self._send(objects.Fail(p.sequence, constants.FAIL_PERM, "Service unavalible."))

	def _description_error(self, p):
		self._send(objects.Fail(p.sequence, constants.FAIL_FRAME, "Packet which doesn't have a possible description."))

	def OnInit(self):
		pass

	def OnConnect(self, p):
		self._send(objects.OK(p.sequence, "Welcome to py-server!"))
		return True

class Server:
	"""\
	Select based, single threaded, polling server.
	"""
	handler = ServerConnection

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
			try:
				ready, trash, errors = select.select([self.s] + self.connections,[],self.connections,1)
			except select.error:
				continue

			for socket in ready:
				if socket is self.s:
					# Accept a new connection
					socket, address = self.s.accept()
					print "Accepting connection from", address
					self.connections.append(self.handler(socket, address, debug=True))
				else:
					try:
						socket.poll()
					except IOError:
						errors.append(socket)
			
			# Cleanup any old sockets
			for socket in errors:
				self.connections.remove(socket)
				del socket

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

