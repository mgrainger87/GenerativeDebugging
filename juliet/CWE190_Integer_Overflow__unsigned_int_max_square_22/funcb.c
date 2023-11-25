 
 

#include "std_testcase.h"

#include <math.h>


 
extern int func_fooGlobal;

void func_fooSink(unsigned int data)
{
    if(func_fooGlobal)
    {
        {
             
            unsigned int result = data * data;
            printUnsignedLine(result);
        }
    }
}


