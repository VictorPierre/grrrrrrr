# An example script to connect to Google using socket
# programming in Python
import socket  # for socket
import sys
from config_connection import host, host_ip

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket successfully created")
except socket.error as err:
    print("socket creation failed with error %s" % err)

try:
    host_ip = socket.gethostbyname(host_ip)
except socket.gaierror:

    # this means could not resolve the host
    print ("there was an error resolving the host")
    sys.exit()

# connecting to the server
s.connect((host_ip, host))

print
"the socket has successfully connected to host %s \
on port == %s" % (host_ip, host)
