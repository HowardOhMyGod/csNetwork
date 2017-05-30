import socket
from packet import *
import time

RTT = 0.1

class Server:
    # create UDP server socket and bind port
    def __init__(self, ip, port):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverSocket.bind((ip, port))
        self.port = port
        self.ip = ip

    # ack logic
    def ackInc(self,seq):
        return seq + 1

    # start server
    def start(self):
        print 'Server ' + self.serverSocket.getsockname()[0] + ' listen on port: ' + str(self.port)

        while True:
            packet, address = self.serverSocket.recvfrom(1024)
            print 'Recievied from client : ', address
            # correct checksum
            if chksum(packet) == 0:
                packet = Packet().unpack(packet)

                # make response packet
                resPacket = Packet(address[1], packet[1])
                resPacket.ack = self.ackInc(packet[2])
                resPacket.src = socket.inet_pton(socket.AF_INET, self.ip)
                resPacket.dst = socket.inet_pton(socket.AF_INET, address[0])

                time.sleep(RTT)
                self.serverSocket.sendto(resPacket.pack(), address)
            else:
                print chksum(packet)

if __name__ == "__main__":
    server = Server('127.0.0.1', 12000)
    server.start()
