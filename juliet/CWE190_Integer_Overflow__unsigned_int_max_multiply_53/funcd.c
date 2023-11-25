 
 

#include "std_testcase.h"


void funcd_fooSink(unsigned int data)
{
    if(data > 0)  
    {
         
        unsigned int result = data * 2;
        printUnsignedLine(result);
    }
}


