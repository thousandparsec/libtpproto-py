# Python Imports
import select
import socket
import sys
import traceback

# Local imports
import objects
constants = objects.constants

from common import Connection, BUFFER_SIZE

socket_error = (socket.error,)
socket_fatal = (IOError,)

class ServerConnection(Connection):
	def __init__(self, s, address, debug=False):
		Connection.__init__(self)

		self.address = address
		self.setup(s, debug=debug, nb=True)

		self.poll = self.initalpoll

	def initalpoll(self):
		"""\
		Checks to see if any packets are on the line
		"""
		print "Inital Poll"
		buffer = self.buffered['bytes-received']
		buffer.write(self.s.recv(BUFFER_SIZE))

		if buffer.peek(2) == "TP":
			if self.debug:
				print "Got a normal tp connection..."
			self.poll = self.tppoll
			return self.poll()

		if buffer.peek(17).startswith("POST /"):
			if self.debug:
				print "Got a http connection..."
			self.s.recv(len(self.buffer)) # Clear all the already recived data...
			self.poll = self.httppoll
			return self.poll()

		# We have gotten to much data, we need to close this connection now
		if buffer.left() > 18:
			raise IOError("No valid connection header found...")

	def httppoll(self):
		print "HTTP Poll"
		buffer = self.buffered['bytes-received']
		buffer.write(self.s.recv(BUFFER_SIZE))

		# FIXME: This is broken
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

		# We have gotten to much data, we need to close this connection now
		if buffer.left() > 1024:
			raise IOError("HTTP Request was to large!")

	def tppoll(self):
		print "TP Poll"
		# Get the packets
		try:
			self._recv(-1)
		except socket_error, e:
			print self, e

		sequences = self.buffered['frames-received'].keys()
		sequences.sort()
		for sequence in sequences:
			p = self._recv(sequence)

			if not p:
				continue

			success = False

			bases = [p.__class__]
			while len(bases) > 0:
				c = bases.pop(0)
				function = "On" + c.__name__

				if hasattr(self, function):
					print function
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

class SSLSocket(object):
	def __init__(self, s, pem):
		global socket_error, socket_fatal
		try:
			import OpenSSL.crypto
			import OpenSSL.SSL as SSL

			context = SSL.Context(SSL.SSLv23_METHOD)
			context.set_verify(SSL.VERIFY_NONE, lambda x: True)
			context.use_certificate(OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, pem))
			context.use_privatekey(OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, pem))

			self.s = SSL.Connection(context, s)

			socket_error = tuple([SSL.WantReadError] + list(socket_error))
			socket_error = tuple([SSL.WantWriteError] + list(socket_error))
			socket_fatal = tuple([SSL.Error] + list(socket_fatal))

			print "Found pyopenssl"
			return
		except ImportError, e:
			print "Unable to import pyopenssl"

		try:
			from tempfile import NamedTemporaryFile
			import M2Crypto
			import M2Crypto.SSL as SSL

			context = SSL.Context('sslv23')
			context.set_verify(SSL.verify_none, 4, lambda x: True)

			f = NamedTemporaryFile(mode='w+b')
			f.write(pem); f.flush()
			context.load_cert(f.name)
			f.close()
			self.s = SSL.Connection(context, s)

			socket_fatal = tuple([SSL.SSLError] + list(socket_fatal))
			return
		except ImportError, e:
			print "Unable to import M2Crypto"
		raise ImportError("Unable to find SSL library")

	def __getattr__(self, key):
		return getattr(self.s, key)

	def __str__(self):
		return object.__str__(self)

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
				try:
					s = SSLSocket(s, pem)
				except ImportError:
					print "Unable to find a SSL library which I can use :/"
					continue

			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			s.bind((address, port))
			s.listen(5)
			s.setblocking(False)

			self.s.append(s)

		self.connections = {}

	def poll(self):
		"""\
		This function is called in the serve_forever loop.

		If data is coming in then it is called every time data is ready to be read.
		Otherwise it should be called at roughly every 100ms.
		"""
		pass

	def serve_forever(self):
		poller = select.poll()
		for s in self.s:
			poller.register(s, select.POLLIN)
			self.connections[s.fileno()] = s

		oldready = []
		while True:
			ready = []
			errors = []

			# Check if there is any socket to accept or with data
			events = poller.poll(100)
			for fileno, event in events:
				if event & select.POLLIN:
					ready.append(self.connections[fileno])
				if event & (select.POLLERR|select.POLLHUP|select.POLLNVAL) > 0:
					errors.append(self.connections[fileno])

			self.poll()

			# Poll any ready sockets..
			for s in ready+oldready:
				if s in self.s:
					# Accept a new connection
					n, address = s.accept()
					print "Accepting connection from %s on %s" % (address, s.getsockname())

					connection = self.handler(n, address, debug=self.debug)
					poller.register(connection, select.POLLIN|select.POLLERR|select.POLLHUP|select.POLLNVAL)
					self.connections[connection.fileno()] = connection
				else:
					# Poll the connection as it's ready
					try:
						s.poll()
						if s in oldready:
							oldready.remove(s)
					except socket_error, e:
						print e
						oldready.append(s)
					except socket_fatal, e:
						print "fatal fallout", s, e
						errors.append(s)

			# Cleanup any old sockets
			for s in errors:
				print "Removing", s
				try:
					s.s.close()
				except Exception, e:
					print "Unable to close socket", e

				try:
					poller.unregister(s)
				except Exception, e:
					print "Unable to unregister socket", e

				del self.connections[s.fileno()]

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

