# Python Imports
import select
import socket
import sys
import traceback

# Local imports
import objects
constants = objects.constants

from common import Connection

socket_error = (socket.error,)
socket_fatal = (IOError,)

class ServerConnection(Connection):
	def __init__(self, s, address, debug=False):
		Connection.__init__(self)

		self.address = address
		self.setup(s, debug=debug, nb=True)

		self.poll = self.initalpoll

	def fileno(self):
		return self.s.fileno()

	def initalpoll(self):
		"""\
		Checks to see if any packets are on the line
		"""
		print "Inital Poll"
		self.buffer += self.s.recv(6)
		
		if self.buffer.startswith("TP"):
			if self.debug:
				print "Got a normal tp connection..."
			self.poll = self.tppoll
			return self.poll()
			
		if self.buffer[-17:].startswith("POST /"):
			if self.debug:
				print "Got a http connection..."
			self.s.recv(len(self.buffer)) # Clear all the already recived data...
			self.poll = self.httppoll
			return self.poll()

		# We have gotten to much data, we need to close this connection now
		if len(self.buffer) > 18:
			raise IOError("No valid connection header found...")

	def httppoll(self):
		print "HTTP Poll"
		if self.buffer.endswith("\r\n\r\n"):
			if self.debug:
				print "Finished the http headers..."
				print self.buffer

			# Send the http headers
			self.s.send("HTTP/1.0 200 OK")
			self.s.send("Cache-Control: no-cache, private\n")
			self.s.send("Content-Type: application/binary\n")
			self.s.send("\n")
			
			self.buffer = ""
			self.poll = self.tppoll	
			return self.poll()
		
		self.buffer += self.s.recv(1)
		
		# We have gotten to much data, we need to close this connection now
		if len(self.buffer) > 1024:
			raise IOError("HTTP Request was to large!")

	def tppoll(self):
		print "TP Poll"
		# Get the packets
		try:
			self._recv(-1)
		except socket_error, e:
			print self, e
		
		sequences = self.buffered['receive'].keys()
		sequences.sort()
		print "tppoll", sequences
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
		
	def _error(self, p):
		type, val, tb = sys.exc_info()
		print ''.join(traceback.format_exception(type, val, tb))
		self._send(objects.Fail(p.sequence, constants.FAIL_FRAME, "Packet wasn't valid."))
		
	def OnInit(self):
		pass

	def OnConnect(self, p):
		self._send(objects.OK(p.sequence, "Welcome to py-server!"))
		return True
		
	def OnPing(self, p):
		self._send(objects.OK(p.sequence, "PONG!"))
		return True

class Server:
	"""\
	Select based, single threaded, polling server.
	"""
	handler = ServerConnection

	def __init__(self, address, port=None, sslport=None, ports=None, sslports=None):

		if ports is None:
			ports = []
		if not port is None:
			ports.append(port)
		
		if sslports is None:
			sslports = []
		if not sslport is None:
			sslports.append(sslport)
	
		self.ports = ports
		self.sslports = sslports

		print "Ports", self.ports, self.sslports

		self.s = []
		for port in ports+sslports:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			if port in sslports:
				pem = """\
-----BEGIN RSA PRIVATE KEY-----
MIIBOwIBAAJBAOTnGJZ1npXzEpchNblVMLOF7Bnv4R+zTrd93nweSEZb6u024o+U
y2Y9s/79f2ytS8csVVxjrFn7Bisw6maXz0MCAwEAAQJAfS7JKpe+l+DsPMyDtgyZ
6sQF4BVo98428XCbuSNSgW8AaWGyqIC1baf0FvNE8OSNrO43Mhqy9C2BG5YQve6K
sQIhAPwHcln2CiPGJ6Rru1SF3MEvC8WImmTrtWVA9IHVNXDbAiEA6IJepK7qvtYc
SoKObjZ+nG0OyGi9b6M9GSO52kWbE7kCIQC7TcV8elB62c+ocLBeVsYDhLVY7vbf
vhWn1KhivVPkNQIhAKaRLwg/n0BT1zSxzyO5un6JyntcPcoKYazu4SgzkWNRAiBn
qEzVAP7TdKkfE2CtVvd2JkGQHQmD7bgOkmhZTIpENg==
-----END RSA PRIVATE KEY-----
-----BEGIN CERTIFICATE-----
MIICTjCCAfigAwIBAgIBADANBgkqhkiG9w0BAQQFADBWMRkwFwYDVQQKExBXZWJt
aW4gV2Vic2VydmVyMRAwDgYDVQQLEwdsZXN0ZXIuMQowCAYDVQQDFAEqMRswGQYJ
KoZIhvcNAQkBFgxyb290QGxlc3Rlci4wHhcNMDQxMDA1MTU0NzQ2WhcNMDkxMDA0
MTU0NzQ2WjBWMRkwFwYDVQQKExBXZWJtaW4gV2Vic2VydmVyMRAwDgYDVQQLEwds
ZXN0ZXIuMQowCAYDVQQDFAEqMRswGQYJKoZIhvcNAQkBFgxyb290QGxlc3Rlci4w
XDANBgkqhkiG9w0BAQEFAANLADBIAkEA5OcYlnWelfMSlyE1uVUws4XsGe/hH7NO
t33efB5IRlvq7Tbij5TLZj2z/v1/bK1LxyxVXGOsWfsGKzDqZpfPQwIDAQABo4Gw
MIGtMB0GA1UdDgQWBBTqK6UJRH7+NpEwgEmJzse910voYTB+BgNVHSMEdzB1gBTq
K6UJRH7+NpEwgEmJzse910voYaFapFgwVjEZMBcGA1UEChMQV2VibWluIFdlYnNl
cnZlcjEQMA4GA1UECxMHbGVzdGVyLjEKMAgGA1UEAxQBKjEbMBkGCSqGSIb3DQEJ
ARYMcm9vdEBsZXN0ZXIuggEAMAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEEBQAD
QQBkj8SEY4RAm9WRDtPJ8qPgmIHeiiwDKsJup1ixsbiQOAV7zG/pMCYM4VWVhmR+
trYiuEhD5HiV/W6DM4WBMg+5
-----END CERTIFICATE-----"""

				SSLFound = False
				while True:
					try:
						import OpenSSL.crypto
						import OpenSSL.SSL as SSL
						SSLFound = True
	
						context = SSL.Context(SSL.SSLv23_METHOD)
						context.set_verify(SSL.VERIFY_NONE, lambda x: True)
						context.use_certificate(OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, pem))
						context.use_privatekey(OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, pem))
	
						s = SSL.Connection(context, s)
	
						global socket_error, socket_fatal
						socket_error = tuple([SSL.WantReadError] + list(socket_error))
						socket_error = tuple([SSL.WantWriteError] + list(socket_error))
						socket_fatal = tuple([SSL.Error] + list(socket_fatal))
						break
					except ImportError, e:
						print "Unable to import pyopenssl"
	
					try:
						from StringIO import StringIO
						from tempfile import NamedTemporaryFile
						import M2Crypto
						import M2Crypto.SSL as SSL
						SSLFound = True
	
						context = SSL.Context('sslv23')
						context.set_verify(SSL.verify_none, 4, lambda x: True)
	
						f = NamedTemporaryFile(mode='w+b')
						f.write(pem); f.flush()
						context.load_cert(f.name)
						f.close()
						s = SSL.Connection(context, s)
	
						global socket_error, socket_fatal
	#					socket_error = tuple([SSL.WantReadError] + list(socket_error))
	#					socket_error = tuple([SSL.WantWriteError] + list(socket_error))
						socket_fatal = tuple([SSL.SSLError] + list(socket_fatal))
						break
					except ImportError, e:
						print "Unable to import M2Crypto"
					
					break

				if not SSLFound:
					print "Unable to find a SSL library which I can use :/"
					continue
			
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			s.bind((address, port))
			s.listen(5)
			s.setblocking(False)

			self.s.append(s)

		self.connections = []
		
	def serve_forever(self):
		oldready = []
		while True:
			# Check if there is any socket to accept or with data
			try:
				ready, trash, errors = select.select(self.s + self.connections,[],self.connections,0.1)
			except select.error:
				continue

			for s in ready+oldready:
				if s in self.s:
					# Accept a new connection
					n, address = s.accept()
					print "Accepting connection from %s on %s" % (address, s.getsockname())
					self.connections.append(self.handler(n, address, debug=self.debug))
				else:
					try:
						s.poll()
						if s in oldready:
							oldready.remove(s)
					except socket_error, e:
						oldready.append(s)
					except socket_fatal, e:
						print "fatal fallout", s, e
						errors.append(s)
				print s, "was ready"
			
			# Cleanup any old sockets
			for s in errors:
				print "Removing", s
				try:
					self.connections.remove(s)
					s.s.close()
				except Exception, e:
					print "Error removing socket", s, e
	
if __name__ == "__main__":
	port = 6924
	while True:
		try:
			s = Server("127.0.0.1", port)
		except:
			print "This port in use...", port
			port += 1
			continue
		s.serve_forever()

