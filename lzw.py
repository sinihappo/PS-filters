#! /usr/bin/env python

import sys
import getopt
import os
import struct
from itertools import count,cycle

dbg = None
# dbg = sys.stderr

def t1():
    return

def usage(utyp, *msg):
    sys.stderr.write('Usage: %s\n' % os.path.split(sys.argv[0])[1])
    if msg:
        sys.stderr.write('Error: %s\n' % (repr(msg),))
    sys.exit(1)

class SE(object):
    def __init__(self,prefix,suffix):
        self.prefix = prefix
        self.suffix = suffix

class LZW(object):
    EOD = 257
    CLR = 256
    MAXSTRINGS = 4096
    None1 = []
    MaxWidth = 12

    def initialize(self):
        self.pd = {}
        for i in range(256):
            self.stra[i] = SE(None,i)
            self.pd[(None,i)] = i
        self.nextIndex = self.EOD + 1
        self.codeWidth = 9

    def __init__(self):
        self.stra = [None] * (2**self.MaxWidth)
        self.acc = 0
        self.bitsInAcc = 0
        self.initialize()
        self.lastcode = None
        return
    def findstring(self,prefix,suffix):
        return self.pd.get((prefix,suffix),self.None1)
        
    def addstring(self,outfile,prefix,suffix):
        self.stra[self.nextIndex] = SE(prefix,suffix)
        self.pd[(prefix,suffix)] = self.nextIndex
        self.nextIndex += 1
        if self.nextIndex >> self.codeWidth:
            self.codeWidth += 1
            if self.nextIndex >> self.MaxWidth:
                self.codeWidth -= 1
                self.sendcode(outfile,self.CLR)
        return
        
    def sendcode(self,outfile,theCode):
        self.acc |= theCode << (32 - self.codeWidth - self.bitsInAcc)
        self.bitsInAcc += self.codeWidth
        while self.bitsInAcc >= 8:
            outfile.write(bytes((self.acc >> 24,)))
            self.acc = (self.acc << 8) & 0xffffffff
            self.bitsInAcc -= 8
        if theCode == self.CLR:
            self.initialize()
        if theCode == self.EOD and self.bitsInAcc != 0:
            outfile.write(bytes((self.acc >> 24,)))

    def readcode(self,infile):
        d = infile.read(1)
        if not d:
            return None
        return d[0]

    def readcodes(self,infile):
        while True:
            d = infile.read(1024)
            if not d:
                return
            for c in d:
                yield c

    def compress(self,infile,outfile):
        self.sendcode(outfile,self.CLR)

        rcodes = self.readcodes(infile)
        if self.lastcode is None:
            self.lastcode = next(rcodes)

        for thiscode in rcodes:
            # ff = self.findstring(self.lastcode,thiscode)
            try:
                ff = self.pd[(self.lastcode,thiscode)]
                self.lastcode = ff
            except KeyError:
                self.sendcode(outfile,self.lastcode)
                self.addstring(outfile,self.lastcode,thiscode)
                self.lastcode = thiscode
            
        if self.lastcode is not None:
            self.sendcode(outfile,self.lastcode)
        self.lastcode = None
        self.sendcode(outfile,self.EOD)
        

class Global:

    def __init__(self):
        self.vflag = 0
        self.hflag = 0
        return
    def doit(self,args):
        if self.hflag:
            sys.stdout.buffer.write(b'%!\ncurrentfile /LZWDecode filter cvx exec\n')

        lz = LZW()

        lz.compress(sys.stdin.buffer,sys.stdout.buffer)
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
