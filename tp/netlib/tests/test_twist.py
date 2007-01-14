
from twisted.trial import unittest
from tp.netlib import twist
from tp.netlib import objects

class TestableConnection(twist.TwistedConnection):
	def __init__(self, *args, **kwargs):
		self.events = []
		twist.TwistedConnection.__init__(self, *args, **kwargs)

class ReceiveBytesConnection(TestableConnection):
	def _recvBytes(self, *args, **kwargs):
		self.events.append(('_recvBytes', args, kwargs))
		return TestableConnection._recvBytes(self, *args, **kwargs)

class ReceiveFrameConnection(TestableConnection):
	def OnOK(self, *args, **kwargs):
		self.events.append(('OnOK', args, kwargs))

class ConnTest(unittest.TestCase):
	def setUp(self):
		self.received = []

	def write(self, data):
		self.received.append(data)

	def test_sendBytes(self):
		self.p = TestableConnection()
		self.p.transport = self

		self.p._sendBytes('foo')
		self.assertEquals(self.received, ['foo'])

	def test_recvBytes(self):
		self.p = ReceiveBytesConnection()
		self.p.transport = self

		validframe = objects.OK(4, '1')
		self.p.dataReceived(str(validframe))
		self.assertEquals(self.p.events, [('_recvBytes', (16,), {'peek': True}), ('_recvBytes', (21L,), {'peek': True}), ('_recvBytes', (21L,), {}), ('_recvBytes', (16,), {'peek': True})])

	def test_recvFrame(self):
		self.p = ReceiveFrameConnection()
		self.p.transport = self

		validframe = objects.OK(4, 'A string about stuff')
		self.p.dataReceived(str(validframe))
		self.assertEquals(self.p.events, [('OnOK', (objects.OK(4, 'A string about stuff'),), {})])

