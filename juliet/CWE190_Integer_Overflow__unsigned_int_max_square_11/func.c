 
 

#include "std_testcase.h"

#include <math.h>


void func_foo()
{
    unsigned int data;
    data = 0;
    if(globalReturnsTrue())
    {
         
        data = UINT_MAX;
    }
    if(globalReturnsTrue())
    {
        {
             
            unsigned int result = data * data;
            printUnsignedLine(result);
        }
    }
}



 

