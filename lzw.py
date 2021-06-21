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

class SE(object):
    def __init__(self,prefix,suffix,next):
        self.prefix = prefix
        self.suffix = suffix
        self.next = next

class LZW(object):
    EOD = 257
    CLR = 256
    MAXSTRINGS = 4096
    None1 = []
    MaxWidth = 12

    def initialize(self):
        self.pd = {}
        for i in range(256):
            self.stra[i] = SE(None,i,None)
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
        index = prefix
        if dbg: dbg.write('findstring %d %d\n' % (prefix,suffix))
        ndx = self.pd.get((prefix,suffix))
        if ndx is not None:
            return ndx
        return self.None1
        while index is not None:
            if dbg: dbg.write('findstring index %d\n' % (index))
            if ((self.stra[index].prefix,self.stra[index].suffix) == (prefix,suffix)):
                return index
            else:
                index = self.stra[index].next
        return self.None1
        
    def addstring(self,outfile,prefix,suffix):
        self.stra[self.nextIndex] = SE(prefix,suffix,self.stra[prefix].next)
        self.pd[(prefix,suffix)] = self.nextIndex
        self.stra[prefix].next = self.nextIndex
        self.nextIndex += 1
        if self.nextIndex >> self.codeWidth:
            self.codeWidth += 1
            if self.nextIndex >> self.MaxWidth:
                self.codeWidth -= 1
                self.sendcode(outfile,self.CLR)
        return
        
    def sendcode(self,outfile,theCode):
        self.acc += theCode << (32 - self.codeWidth - self.bitsInAcc)
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
        for code in self.readcodes(infile):
            if self.lastcode is None:
                self.lastcode = code
                if not self.lastcode:
                    break
                continue

            thiscode = code
            if not thiscode:
                break

            ff = self.findstring(self.lastcode,thiscode)
            if ff is not self.None1:
                self.lastcode = ff
            else:
                self.sendcode(outfile,self.lastcode)
                self.addstring(outfile,self.lastcode,thiscode)
                self.lastcode = thiscode
            
        if self.lastcode:
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
