 
 

#include "std_testcase.h"


void funcb_fooSink(unsigned int * dataPtr)
{
    unsigned int data = *dataPtr;
    if(data > 0)  
    {
         
        unsigned int result = data * 2;
        printUnsignedLine(result);
    }
}


