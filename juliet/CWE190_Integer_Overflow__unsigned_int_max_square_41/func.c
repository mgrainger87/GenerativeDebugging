 
 

#include "std_testcase.h"

#include <math.h>


static void fooSink(unsigned int data)
{
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
    fooSink(data);
}



 

