#! /usr/bin/env python

import sys
import getopt
import os
import struct
from itertools import count,cycle

def usage(utyp, *msg):
    sys.stderr.write('Usage: %s\n' % os.path.split(sys.argv[0])[1])
    if msg:
        sys.stderr.write('Error: %s\n' % (repr(msg),))
    sys.exit(1)

class NWriter(object):
    def __init__(self,ofile,nchars):
        self.ofile = ofile
        self.nchars = nchars
        self.nn = 0
        return
    def write(self,s):
        while s or self.nn >= self.nchars:
            if self.nn >= self.nchars:
                self.ofile.write('\n')
                self.nn = 0
            s0,s = s[:self.nchars-self.nn],s[self.nchars-self.nn:]
            self.ofile.write(s0)
            self.nn += len(s0)
    def nl(self):
        if self.nn:
            self.ofile.write('\n')
            self.nn = 0

class Global:
    base85digits = ''.join(chr(i) for i in range(33,33+85))
    divarray = tuple(85**i for i in range(5))
    def __init__(self):
        self.vflag = 0
        self.hflag = 0
        return
    def encode(self,infile,outfile):
        unpack = struct.unpack
        ofl = NWriter(outfile,76)
        while True:
            d = infile.read(4)
            if not d:
                break
            lend = len(d)
            while len(d) < 4:
                d = d+b'\x00'
            base256 = unpack('>I',d)[0]
            digits = ''.join(self.base85digits[(base256 // self.divarray[i]) % 85] for i in range(4,-1,-1))
            ofl.write(digits[:lend+1])
        # ofl.nl()
        outfile.write('~>\n')
    def doit(self,args):
        if self.hflag:
            sys.stdout.buffer.write(b'%!\ncurrentfile /ASCII85Decode filter cvx exec\n')
        self.encode(sys.stdin.buffer,sys.stdout)
        return

def main(argv):
    gp = Global()
    try:
        opts, args = getopt.getopt(argv[1:],
                                   'hv',
                                   ['header',
                                    'verbose',
                                    ])
    except getopt.error as msg:
        usage(1, msg)

    for opt, arg in opts:
        if opt in ('-h', '--header'):
            gp.hflag += 1
        elif opt in ('-v', '--verbose'):
            gp.vflag += 1

    gp.doit(args)
        
if __name__ == '__main__':
    main(sys.argv)
