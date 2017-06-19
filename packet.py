import struct
import socket
import string
import random

tcp_format = '!2H2Ih3bH'
BUFFER_SIZE = 10240

class Packet:
    def __init__(self, sport = 0, dport = 0):
        # TCP packet
        self.sport = sport
        self.dport = dport
        self.seq = 0
        self.ack = 0
        self.chksum = 0

        # initial and close connection
        self.ACK = 0
        self.SYN = 0
        self.FIN = 0

        # IP packet
        self.dst = 0
        self.src = 0

        #rcv_window
        self.rwnd = BUFFER_SIZE

        #SACK
        self.sack_permit = 1
        self.l1 = -1
        self.r1 = -1
        self.l2 = -1
        self.r2 = -1
        self.l3 = -1
        self.r3 = -1


    # pack tcp and ip packet
    def pack(self, data = ''):
        # ip to str
        self.src = socket.inet_pton(socket.AF_INET, self.src)
        self.dst = socket.inet_pton(socket.AF_INET, self.dst)

        tcp_packet = struct.pack(tcp_format, self.sport, self.dport, self.seq, self.ack, self.chksum, self.ACK, self.SYN, self.FIN, self.rwnd)
        ip_pkt = struct.pack('!4s4s', self.src, self.dst)
        sack_opt = struct.pack('!H6i', self.sack_permit, self.l1, self.r1, self.l2, self.r2, self.l3, self.r3)

        if data != '':
            payload = ''
            for i in range(len(data)):
                payload += struct.pack('!c', data[i])

            checksum = chksum(tcp_packet + ip_pkt + payload)
            return struct.pack(tcp_format, self.sport, self.dport, self.seq, self.ack, checksum, self.ACK, self.SYN, self.FIN, self.rwnd) + ip_pkt + sack_opt + payload

        else:
            checksum = chksum(tcp_packet + ip_pkt)
            return struct.pack(tcp_format, self.sport, self.dport, self.seq, self.ack, checksum, self.ACK, self.SYN, self.FIN, self.rwnd) + ip_pkt + sack_opt


    # unpack TCP packet and IP packet
    def unpack(self, packet, plen = 0):
        if plen == 0:
            pkt = list(struct.unpack('!2H2Ih3bH4s4sH6i', packet))
        else:
            pkt = list(struct.unpack('!2H2Ih3bH4s4sH6i{}c'.format(plen), packet))
        pkt[9] = socket.inet_ntop(socket.AF_INET, pkt[9])
        pkt[10] = socket.inet_ntop(socket.AF_INET, pkt[10])
        return tuple(pkt)


    def makeData(self):
        output = ''
        data_set = string.letters + '1234567890'

        for i in range(10240):
            c = struct.pack('!c', random.choice(data_set))
            output += c

        return output
def chksum(pkt):
    def carry_around_add(a, b):
        c = a + b
        return (c & 0xffff) + (c >> 16)

    if len(pkt) % 2 != 0:
        pkt += '\0'

    s = 0
    for i in range(0, len(pkt), 2):
        w = (ord(pkt[i]) << 8 ) + ord(pkt[i+1])
        s = carry_around_add(s, w)
    return ~s & 0xfff

if __name__ == "__main__":
    pass
