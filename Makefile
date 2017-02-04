all:	lzw ascii85

lzw:	lzw.o
	$(CC) -o lzw lzw.o

ascii85:	ascii85.o
	$(CC) -o ascii85 ascii85.o
