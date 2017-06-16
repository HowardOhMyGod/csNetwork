import socket
import struct
from packet import *
import time

nat_table = {
    '127.0.0.3:2000': '127.0.0.5:3000',
    '127.0.0.4:2100': '127.0.0.6:3000'
}

TCP = '!2Ih3bH'
PORT = '!2H'
IP = '!4s4s'

RTT = 0.1

# client side NAT
class NAT:
    def __init__(self):
        self.natSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.natSocket.bind(('127.0.0.8', 1500))

        print 'Nat router listen for incoming packet...'

    def start(self):
        while True:
            pkt, addr = self.natSocket.recvfrom(10240)
            port, tcp_pkt, ip, data_pkt = self.getIpAndPort(pkt)
            print 'Receive packet from ', addr

            # client send to server
            if ip[0] + ':' + str(port[0]) in nat_table:
                pkt = self.sendToServer(pkt)
                print '       Send a packet to {0} : {1}'.format(ip[1], port[1])
                self.natSocket.sendto(pkt, (ip[1], port[1]))

            # server send to client
            elif self.findkeybyval(ip[1] + ':' + str(port[1])):
                pkt = self.sendToClient(pkt)
                port, tcp_pkt, ip, data_pkt = self.getIpAndPort(pkt)

                print '       Send a packet to {0} : {1}'.format(ip[1], port[1])
                self.natSocket.sendto(pkt, (ip[1], port[1]))
            else:
                print ip, port



    def getIpAndPort(self, pkt):
        # packet size
        tcp_size = struct.calcsize(TCP)
        ip_size = struct.calcsize(IP)
        port_size = struct.calcsize(PORT)

        # extract ip datagram and TCP segment get src, dst, sport, dport
        ip_pkt = struct.unpack(IP, pkt[port_size + tcp_size: port_size + tcp_size + ip_size])
        ip = []
        ip.append(socket.inet_ntop(socket.AF_INET, ip_pkt[0]))
        ip.append(socket.inet_ntop(socket.AF_INET, ip_pkt[1]))

        port_pkt = struct.unpack(PORT, pkt[:port_size])

        # slice packet and not unpack
        tcp_pkt = pkt[port_size: port_size + tcp_size]
        payload = pkt[port_size + tcp_size + ip_size:]


        return list(port_pkt), tcp_pkt, ip, payload

    def modifyCksum(self, pkt):
        cksum = struct.pack('!h', 0)
        head = pkt[:12]
        tail = pkt[14:]

        before_cksum_pkt = head + cksum + tail
        cksum = struct.pack('!h', chksum(before_cksum_pkt))

        return head + cksum + tail

    def packIP(self, src, dst):
        src = socket.inet_pton(socket.AF_INET, src)
        dst = socket.inet_pton(socket.AF_INET, dst)

        return struct.pack(IP, src, dst)

    # send nat
    def sendToServer(self, pkt):
        port, tcp_pkt, ip, data_pkt = self.getIpAndPort(pkt)
        saddr = ip[0] + ':' + str(port[0])

        # repack packet with nat src and port and update chksum
        if saddr in nat_table:
            nat_src = nat_table[saddr].split(':')[0] # get nat src
            nat_port = int(nat_table[saddr].split(':')[1]) # get nat port

            port_pkt = struct.pack(PORT, nat_port, port[1])
            ip_pkt = self.packIP(nat_src, ip[1])

            temp_pkt = port_pkt + tcp_pkt + ip_pkt + data_pkt

            return self.modifyCksum(temp_pkt)
        else:
            # return original pkt
            return self.pkt

    # recieve nat
    def sendToClient(self, pkt):
        port, tcp_pkt, ip, data_pkt = self.getIpAndPort(pkt)
        daddr = ip[1] + ':' + str(port[1])

        if daddr in nat_table.values():
            # find origin ip
            nat_dst = self.findkeybyval(daddr).split(':')[0]
            nat_port = int(self.findkeybyval(daddr).split(':')[1])

            port_pkt = struct.pack(PORT, port[0], nat_port)
            ip_pkt = self.packIP(ip[0], nat_dst)

            temp_pkt = port_pkt + tcp_pkt + ip_pkt + data_pkt

            return self.modifyCksum(temp_pkt)
        else:
            return self.pkt

    def findkeybyval(self, val):
        for ip, nat in nat_table.iteritems():
            if val == nat:
                return ip
        return None

if __name__ == '__main__':
    router = NAT()
    router.start()
