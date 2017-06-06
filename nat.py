import socket
import struct
from packet import *

nat_table = {
    '127.0.0.3:2000': '127.0.0.5:3000',
    '127.0.0.4:2100': '127.0.0.5:4000'
}

# client side NAT
class NAT:
    def __init__(self, pkt):
        packet = struct.unpack('!2H2Ih4s4s', pkt)

        self.origin_pkt = pkt
        self.sport = packet[0]
        self.dport = packet[1]
        self.seq = packet[2]
        self.ack = packet[3]
        self.cksum = 0
        self.src = packet[5] # pack ip
        self.dst = packet[6] # pack ip

    # send nat
    def sendToServer(self):
        src = socket.inet_ntop(socket.AF_INET, self.src)
        saddr = str(src) + ':' + str(self.sport) # source ip and port

        # repack packet with nat src and port and update chksum
        if saddr in nat_table:
            nat_src = socket.inet_pton(socket.AF_INET, nat_table[saddr].split(':')[0]) # get nat src
            nat_port = int(nat_table[saddr].split(':')[1]) # get nat port

            temp_pkt = struct.pack('!2H2Ih4s4s', nat_port, self.dport, self.seq, self.ack, self.cksum, nat_src, self.dst)
            self.cksum = chksum(temp_pkt)

            return struct.pack('!2H2Ih4s4s', nat_port, self.dport, self.seq, self.ack, self.cksum, nat_src, self.dst)
        else:
            return self.origin_pkt

    # recieve nat
    def sendToClient(self):
        dst = socket.inet_ntop(socket.AF_INET, self.dst)
        daddr = str(dst) + ':' + str(self.dport) # dest ip and port

        if daddr in nat_table.values():
            # find origin ip
            nat_dst = socket.inet_pton(socket.AF_INET, self.findkeybyval(daddr).split(':')[0])
            nat_port = int(self.findkeybyval(daddr).split(':')[1])

            temp_pkt = struct.pack('!2H2Ih4s4s', self.sport, nat_port, self.seq, self.ack, self.cksum, self.src, nat_dst)
            self.cksum = chksum(temp_pkt)

            return struct.pack('!2H2Ih4s4s', self.sport, nat_port, self.seq, self.ack, self.cksum, self.src, nat_dst)
        else:
            return self.origin_pkt


    def findkeybyval(self, val):
        for ip, nat in nat_table.iteritems():
            if val == nat:
                return ip
        return None

if __name__ == '__main__':
    pkt = Packet()
    pkt.sport = 12000
    pkt.dport = 3000
    pkt.dst = socket.inet_pton(socket.AF_INET, '127.0.0.5')
    pkt.src = socket.inet_pton(socket.AF_INET, '127.0.0.1')

    p = pkt.pack()
    print 'origin packet : ', Packet().unpack(p)
    n = NAT(p)
    print 'nat packet : ', Packet().unpack(n.sendToClient())
    print 'nat ip :', socket.inet_ntop(socket.AF_INET, Packet().unpack(n.sendToClient())[6])
    print 'cksum: ', chksum(n.sendToClient())
