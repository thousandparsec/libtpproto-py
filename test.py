

from tests.python.OK_tests import tests as OK_tests
from tests.python.Fail_tests import tests as Fail_tests
from tests.python.Sequence_tests import tests as Sequence_tests
from tests.python.Connect_tests import tests as Connect_tests
from tests.python.Login_tests import tests as Login_tests
from tests.python.Object_GetById_tests import tests as Object_GetById_tests
from tests.python.Object_GetByPos_tests import tests as Object_GetByPos_tests
from tests.python.Object_tests import tests as Object_tests

print "OK"
for t in OK_tests:
	t, error = t()
	print "	", error
	
print "Fail"
for t in Fail_tests:
	t, error = t()
	print "	", error
	
print "Sequence"
for t in Sequence_tests:
	t, error = t()
	print "	", error

print "Connect"
for t in Connect_tests:
	t, error = t()
	print "	", error

print "Login"
for t in Login_tests:
	t, error = t()
	print "	", error

print "Object_GetById"
for t in Object_GetById_tests:
	t, error = t()
	print "	", error

print "Object_GetByPos"
for t in Object_GetByPos_tests:
	t, error = t()
	print "	", error

print "Object"
for t in Object_tests:
	t, error = t()
	print "	", error
	
