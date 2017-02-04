/*
 * PSLZW.C
 *
 * UNIX LZW compression filter for Adobe level-2 PostScript
 *
 * 1991 Tektronix, Inc., K. Draz, Tektronix Application Engineering
 *
 * Permission is granted to use this code for any purpose.
 * 
 */

#include <stdio.h>

/* Various constants
 */
	 
#define EOD			  257			  /* End of Data marker */
#define CLR			  256			  /* Clear Table Marker */
#define MAXSTRINGS  4096		  /* using 12 bit max codes */
#define TRUE		  (1==1)
#define FALSE		  !TRUE
	 
/* This is the structure for a single entry into the string table
 */
	 
typedef struct
{
	 short prefix;		
	 short suffix;
	 short next;
} stringrec;

/* Global data
 */

int codeWidth = 9, bitsInAcc = 0;	/* Used by code send function */
unsigned long acc;						/* =bits left over from a sendcode */
int nextIndex;								/* Used by newentry function */
stringrec stringarray[4096];			/* This is the string table */
long incount = 0, outcount = 0;		/* Input/output tally */


void Initialize(void);
void SendCode(short theCode);
int FindString(short *prefix, short suffix);
int main(int argc, char *argv[]);
void AddString(short prefix, short suffix);
void ShowStats(void);
	 
int	hflag;
int	vflag;

void Initialize()
{
	 int index;

	 if (vflag) {
	   fprintf(stderr,"\rInitializing\n");
	 }
	 for(index = 0; index < 256; index++)
	 {
		  stringarray[index].prefix = -1;
		  stringarray[index].suffix = (char) index;
		  stringarray[index].next = -1;
	 }
	 nextIndex = EOD + 1;
	 codeWidth = 9;
}
	 
void SendCode(short theCode)
{
	 acc += (long) theCode << (32 - codeWidth - bitsInAcc);
	 bitsInAcc += codeWidth;
	 while(bitsInAcc >= 8)
	 {
		  fputc(acc >> 24, stdout);
		  acc = acc << 8;
		  bitsInAcc -= 8;
		  outcount++;
	 }

	 if(theCode == CLR)
	 {
		  Initialize();
	 }

	 if(theCode == EOD && bitsInAcc != 0)
	 {
		  fputc(acc >> 24, stdout);
		  outcount++;
	 }

	 return;
}

int main(int argc, char *argv[])
{
	 short lastCode;
	 short thisCode;
	 double comppct;
	 int	c;

	 while ((c = getopt(argc,argv,"hv")) != EOF) {
	   switch (c) {
	   case 'h':
	     hflag++;
	     break;
	   case 'v':
	     vflag++;
	     break;
	   }
	 }

	 if (hflag)
	   {
	     fputs("%!\ncurrentfile /LZWDecode filter cvx exec\n",stdout);
	     incount += 41;
	     fflush(stdout);
	   }
	 
	 if (vflag) {
	   fprintf(stderr, "\nCompressing...");
	   fflush(stderr);
	 }
	 
	 SendCode(CLR);
	 
	 if((lastCode = fgetc(stdin)) == EOF)
	 {
		  ++incount;
		  SendCode(EOD);
  		  return;
	 }
	 
	 while((thisCode = fgetc(stdin)) != EOF)
	 {
		  if(!(++incount & 0x00004FFF))
		  {
				if (vflag) ShowStats();
		  }

		  if(FindString(&lastCode, thisCode))
		  {
				continue;
		  } else
		  {
				SendCode(lastCode);
				AddString(lastCode, thisCode);
				lastCode = thisCode;
		  }

	 }

	 SendCode(lastCode);
	 SendCode(EOD);

	 if (vflag) {
	   ShowStats();
	   fprintf(stderr, "\nDone.\n");
	   fflush(stderr);
	 }
	 
	 return 0;
}

int FindString(short *prefix, short suffix)
{
	 short index = *prefix;

	 while(index != -1)
	 {
		  if(stringarray[index].prefix == *prefix &&
			  stringarray[index].suffix == suffix)
		  {
				*prefix = index;
				return(TRUE);
		  } else
		  {
				index = stringarray[index].next;
		  }
	 }

	 return(FALSE);
}

void AddString(short prefix, short suffix)
{
	 
	 stringarray[nextIndex].prefix = prefix;
	 stringarray[nextIndex].suffix = suffix;
	 stringarray[nextIndex].next = stringarray[prefix].next;
	 stringarray[prefix].next = nextIndex;

	 if(++nextIndex >> codeWidth)
	 {
		  if(++codeWidth > 12)
		  {
				--codeWidth;
				SendCode(CLR);
		  }
	 }
	 return;
}

void ShowStats()
{
	 double comppct;
	 
	 comppct = 100.0 * (1.0 - (double) outcount / (double) incount);
	 fprintf(stderr, "\rCompressing: %d bytes input, %d bytes output, %3.2f%% saved.",
				incount, outcount, comppct);
	 fflush(stderr);
}
