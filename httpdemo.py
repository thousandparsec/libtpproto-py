
import client
import server

c = client.ClientConnection("http://127.0.0.1:6923")
#c = client.ClientConnection("http://mithro.dyndns.org")
c.connect()
