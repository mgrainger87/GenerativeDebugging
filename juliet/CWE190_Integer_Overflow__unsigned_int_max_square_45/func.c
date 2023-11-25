 
 

#include "std_testcase.h"

#include <math.h>

static unsigned int func_fooData;
static unsigned int func_goodG2BData;
static unsigned int func_goodB2GData;


static void fooSink()
{
    unsigned int data = func_fooData;
    {
         
        unsigned int result = data * data;
        printUnsignedLine(result);
    }
}

void func_foo()
{
    unsigned int data;
    data = 0;
     
    data = UINT_MAX;
    func_fooData = data;
    fooSink();
}



 
