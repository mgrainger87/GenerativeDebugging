 
 

#include "std_testcase.h"


void func_foo()
{
    unsigned int data;
    data = 0;
     
    data = UINT_MAX;
    {
        unsigned int dataCopy = data;
        unsigned int data = dataCopy;
        {
             
            unsigned int result = data + 1;
            printUnsignedLine(result);
        }
    }
}



 
