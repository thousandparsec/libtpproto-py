#! /usr/bin/python

import time

import connection
c = connection.Connection("127.0.0.1")
print "Connect:", c.connect()
print "Login:", c.login("mithro", "peanut")
print "Object 0:", str(c.get_objects(0))
print "Object 0,1:", str(c.get_objects([0,1]))
print "Disconnect:", c.disconnect()

c = connection.Connection("127.0.0.1", nb=1)
c.connect()
c.login("mithro", "peanut")
c.get_objects(0)
c.get_objects([0,1])
time.sleep(1)
print "Connect:", c.poll()
print "Login:", c.poll()
print "Object 0:", c.poll()
print "Object 0,1:", c.poll()
print "Disconnect:", c.disconnect()
