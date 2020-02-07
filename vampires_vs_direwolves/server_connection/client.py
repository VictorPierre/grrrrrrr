# An example script to connect to Google using socket
# programming in Python
import socket  # for socket
import sys
from server_connection.config_connection import port, host_ip


def connect():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket successfully created")
    except socket.error as err:
        print("socket creation failed with error %s" % err)
        return
    try:
        host = socket.gethostbyname(host_ip)
    except socket.gaierror as err:
        # this means could not resolve the host
        print("there was an error resolving the host")
        print(err)
        return

    # connecting to the server
    sock.connect((host, port))
    return sock


if __name__ == '__main__':
    sock = connect()
    print(f"the socket has successfully connected to host {host_ip} on port {port}")
