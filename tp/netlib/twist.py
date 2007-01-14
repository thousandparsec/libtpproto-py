
import sys, traceback

from twisted.internet import protocol, reactor

import xstruct

from common import ConnectionCommon, StringQueue
from objects import Fail
from support.output import red, green

class TwistedConnection(ConnectionCommon, protocol.Protocol):
	def __init__(self, *args, **kw):
		ConnectionCommon.__init__(self)
		self.buffered['bytes-received'] = StringQueue()

	def _sendBytes(self, bytes=''):
		"""\
		Send bytes onto the socket.
		"""
		if self.debug and len(bytes) > 0:
			green("Sending: %s \n" % xstruct.hexbyte(bytes))
		self.transport.write(bytes)

	def _recvBytes(self, size, peek=False):
		"""\
		Receive a bunch of bytes onto the socket.
		"""
		buffer = self.buffered['bytes-received']
		if len(buffer) < size:
			return ''
		else:
			return [buffer.read, buffer.peek][peek](size)

	def dataReceived(self, data):
		"""\
		"""
		if self.debug and len(data) > 0:
			red("Received: %s \n" % xstruct.hexbyte(data))

		# Push the data onto the buffer
		buffer = self.buffered['bytes-received']
		buffer.write(data)

		self._recvFrame(-1)

		sequences = self.buffered['frames-received'].keys()
		sequences.sort()

		for sequence in sequences:
			p = self._recvFrame(sequence)
			if not p:
				continue

			bases = [p.__class__]
			while len(bases) > 0:
				c = bases.pop(0)
				function = "On" + c.__name__

				if hasattr(self, function):
					try:
						success = getattr(self, function)(p)
					except:
						type, val, tb = sys.exc_info()
						print ''.join(traceback.format_exception(type, val, tb))
					break
				else:
					print "No handler for packet of %s" % c.__name__

				bases += list(c.__bases__)
			if len(bases) == 0:
				self._sendFrame(Fail(p.sequence, 2, "Service Unavailable..."))

class TwistedFactory(protocol.ServerFactory):
    protocol = TwistedConnection

def run():
	from twisted.internet import reactor
	reactor.listenTCP(6923, TwistedFactory())
	reactor.run()

if __name__ == "__main__":
	run()

