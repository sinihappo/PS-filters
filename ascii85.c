#include <stdio.h>

/* powers of 85 */

long divarray[5] = { (long) 1, (long) 85, (long) 7225, (long) 614125,
						   (long) 52200625 };
	 
#include <stdio.h>
#include <unistd.h>

int	vflag;
int	hflag;

extern void EncodeFile(void);

int
main(argc,argv)

int argc;
char **argv;

{
  int	c;
  
  while ((c = getopt(argc,argv,"vh")) != EOF) {
    switch (c) {
    case 'v':
      vflag++;
      break;
    case 'h':
      hflag++;
      break;
    }
  }
  if (hflag)
    fputs("%!\ncurrentfile /ASCII85Decode filter cvx exec\n",stdout);
  
  EncodeFile();
  return(0);
}

#define myputc(c,f,counter,maxcounter) (putc(c,f), (counter)++, ((counter) >= (maxcounter)) ? (putc('\n',f),counter=0) : 0)

void
EncodeFile()
{
  unsigned long base256 = 0;
  int phase = 0, theChar, nonzero, base85digit[5], index, nz;
  long inbytes = 0;
  long outbytes = 0;
  int	ochars = 0;
  int	maxochars = 76;
	 
  while((theChar = fgetc(stdin)) != EOF)
    {
      inbytes++;
      base256 += ((unsigned long)theChar) << (8 * (3 - phase++));
      
      if(phase == 4)
	{
	  for(index = 4; index >= 0; index--)
	    {
	      if((base85digit[index] = base256 / divarray[index]) != 0)
		{
		  nz = !0;
		}
	      base256 = base256 % divarray[index];
	    }
	  
	  if(nz)
	    {
	      for(index = 4; index >= 0; index--)
		{
		  myputc(base85digit[index] + '!', stdout,ochars,maxochars);
		  outbytes++;
		}
	    } else
	    {
	      myputc('z', stdout,ochars,maxochars);
	      outbytes++;
	    }
	  phase = 0;
	  base256 = 0;
	}
      
      if((inbytes & 0x0000FFFF) == 0x0000FFFF)
	{
	  if (vflag) {
	    fprintf(stderr, "\r%ld bytes in, %ld bytes out", inbytes, outbytes);
	    fflush(stderr);
	  }
	}
    }
  
  if(phase != 0)
    {
      for(index = 4; index >= (4-phase); index--)
	{
	  myputc(base256 / divarray[index] + '!', stdout,ochars,maxochars);
	  base256 = base256 % divarray[index];
	}
    }
  
  fprintf(stdout, "~>\n");
  
  fflush(stdout);
  return;
}
