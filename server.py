# Python Imports
import sys
import socket
import SocketServer

# Local imports
import xstruct
import objects
constants = objects.constants

from common import Connection

class ServerConnection(Connection, SocketServer.BaseRequestHandler):
	def __init__(self, request, client_address, server):
		print request, client_address, server
		
		self.server = server
		self.address = client_address

		try:
			self.setup(request)
			self.handle()
			self.finish()
		finally:
			sys.exc_traceback = None	# Help garbage collection

	def handle(self):
		"""\
		Checks to see if any packets are on the line
		"""
		print "Handle..."
		self.OnInit()
		
		self.working = True
		while self.working:

			# Get the packets
			try:
				self._recv(-1)
			except:
				self._send(objects.Fail(1, constants.FAIL_PROTOCOL, "Bad packet."))
				break
			
			for packet in self.rbuffer.items():

				success = False
				for c in [packet.__class__.__name__] + packet.__class__:
					function = "On" + c.__name__
	
					if hasattr(self, function):
						success = function(packet)
						break
				
				if not success:
					self._send(objects.Fail(packet.no, constants.FAIL_PERM, "Service unavalible."))

	def exit(self):
		self.working = False

	def _description_error(self, packet):
		self._send(objects.Fail(packet.no, constants.FAIL_FRAME, "Packet which doesn't have a possible description."))

	def OnInit(self):
		pass

	def OnConnect(self, packet):
		self._send(object.OK(packet.no, "Welcome to py-server!"))
		return True

def Server(address="", port=6923):
	return SocketServer.ThreadingTCPServer((address, port), ServerConnection)

if __name__ == "__main__":
	port = 6923
	while True:
		try:
			s = Server(port=port)
		except:
			print "This port in use...", port
			port += 1
			continue
		s.serve_forever()

