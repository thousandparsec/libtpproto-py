
import sys

def red(string, flush=1):
	sys.stdout.write("[01;32m")
	sys.stdout.write(string)
	sys.stdout.write("[0m")
	if flush:
		try:
			sys.stdout.flush()
		except:
			pass

def green(string, flush=1):
	sys.stdout.write("[01;31m")
	sys.stdout.write(string)
	sys.stdout.write("[0m")
	if flush:
		try:
			sys.stdout.flush()
		except:
			pass
