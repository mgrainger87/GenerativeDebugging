 
 

#include "std_testcase.h"


void funcc_fooSink(unsigned int data)
{
    if(data > 0)  
    {
         
        unsigned int result = data * 2;
        printUnsignedLine(result);
    }
}


