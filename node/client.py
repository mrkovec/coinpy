import logging
import socket
import sys
import threading

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



# # Echo server program
# import socket
#
# HOST = ''                 # Symbolic name meaning all available interfaces
# PORT = 50007              # Arbitrary non-privileged port
# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.bind((HOST, PORT))
#     s.listen(1)
#     conn, addr = s.accept()
#     with conn:
#         print('Connected by', addr)
#         while True:
#             data = conn.recv(1024)
#             if not data: break
#             conn.sendall(data)
# # Echo client program
# import socket
#
# HOST = 'daring.cwi.nl'    # The remote host
# PORT = 50007              # The same port as used by the server
# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect((HOST, PORT))
#     s.sendall(b'Hello, world')
#     data = s.recv(1024)
# print('Received', repr(data))


        # s.shutdown()
        # s.close()

#
# class Msg(object):
#     def __init__(self, cls: List[(str, int)]) -> None:
#         pass
#
# class Client(object):
#     def __init__(self, port: int) -> None:
#         self.listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         self.listener.bind((socket.gethostname(), port))
#         self.listener.listen(5)
#         self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#
#     def listen(self) -> None:
#         while True:
#             (clientsocket, address) = self.listener.accept()
#             chunk = clientsocket.recv(2048)
#             logger.debug(chunk.decode() + ' from:')
#             logger.debug(clientsocket.getpeername()[0])
#
#     def connect(self, host, port):
#         self.sock.connect((host, port))
#
#     def mysend(self, msg):
#         sent = self.sock.sendall(msg.encode('utf-8'))
#         if sent == 0:
#             raise RuntimeError("socket connection broken")
#
#     def myreceive(self):
#         chunk = self.sock.recv(2048)
#         if chunk == b'':
#             raise RuntimeError("socket connection broken")
#         ip = self.sock.getpeername()[0]
#         print(ip)
#         return chunk.decode()
