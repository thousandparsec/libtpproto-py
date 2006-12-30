#!/usr/bin/python2
#
# Bonjour browsing sample
# 
# Usage: python browse.py <serviceType>
#
# e.g.python browse.py _daap._tcp


import sys
import bonjour
import select
import socket
import struct

from browse import ZeroConfBrowser as ZeroConfBrowserBase

escaping= {
	r'\.': '.',
	r'\032': ' ',
}

class ZeroConfBrowser(ZeroConfBrowserBase):
	def txt2dict(self, txt):
		bits = []
		while len(txt) > 0:
			l = struct.unpack('!b', txt[0])[0]
			bits.append(txt[1:l+1])
			txt = txt[l+1:]
		properties = {}
		for bit in bits:
			r = bit.split('=')
			properties[r[0]] = "=".join(r[1:])
		return properties	

	# Callback for service resolving
	def ResolveCallback(self, sdRef, flags, interfaceIndex, errorCode, fullname, hosttarget, port, txtLen, txtRecord, userdata):
		fullname = unicode(fullname, 'utf-8')

		# Cleanup and split the fullname
		i = fullname.find('.')
		while fullname[i-1] == '\\' and i > 0 and i <= (len(fullname)-1):
			i = fullname.find('.', i+1)

		name, type = fullname[:i], fullname[i+1:-1]

		# Replace the escaped values
		for fom, to in escaping.items():
			name = name.replace(fom, to)

		addr = (hosttarget[:-1], socket.gethostbyname(hosttarget), port)
		details = self.txt2dict(txtRecord)
		self.ServiceFound(name, type.split('.')[0][1:], addr, details, details)

	# Callback for service browsing
	def BrowseCallback(self, sdRef,flags,interfaceIndex,
				 errorCode,serviceName,regtype,
				 replyDomain,
				 userdata):
		if flags & bonjour.kDNSServiceFlagsAdd:
			sdRef2 = bonjour.AllocateDNSServiceRef()
			ret = bonjour.pyDNSServiceResolve(sdRef2,
											0,
											0,
											serviceName,
											regtype,
											replyDomain,
											self.ResolveCallback,
											None );

			bonjour.DNSServiceProcessResult(sdRef2)
		elif flags == 0:
			self.ServiceGone(serviceName, regtype.split('.')[0][1:], None)

	def __init__(self):
		ZeroConfBrowserBase.__init__(self)
		self._exit = False
	
	def exit(self):
		self._exit = True

	def run(self):
		serviceRefs = {}
		for stype in ['_tp', '_tps', '_tphttp', '_tphttps']:
			stype = stype+'._tcp'
			print "registering for", stype
			# Allocate a service discovery ref and browse for the specified service type
			serviceRef = bonjour.AllocateDNSServiceRef()
			ret = bonjour.pyDNSServiceBrowse(	serviceRef, # DNSServiceRef		 *sdRef,
												0,			# DNSServiceFlags	 flags,						
												0,			# uint32_t			interfaceIndex,			 
												stype, 		# const char			*regtype,					 
												'local.',				# const char			*domain,	/* may be NULL */ 
												self.BrowseCallback,	# DNSServiceBrowseReply callBack,					 
												None)
			if ret != bonjour.kDNSServiceErr_NoError:
				print "ret = %d; exiting" % ret

			fd = bonjour.DNSServiceRefSockFD(serviceRef)
			serviceRefs[fd] = serviceRef

		# Get socket descriptor and loop					 
		while not self._exit:
			ret = select.select(serviceRefs.keys(),[],[], 0.5)
			for fd in ret[0]:
				ret = bonjour.DNSServiceProcessResult(serviceRefs[fd])
				if ret != bonjour.kDNSServiceErr_NoError:
					print "ret = %d; exiting" % ret

		# Deallocate the service discovery ref
		bonjour.DNSServiceRefDeallocate(serviceRef)

def main():
	a = ZeroConfBrowser()
	a.run()

if __name__ == "__main__":
	main()
