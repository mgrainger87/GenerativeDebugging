 
 

#include "std_testcase.h"


static void fooSink(unsigned int data)
{
    if(data > 0)  
    {
         
        unsigned int result = data * 2;
        printUnsignedLine(result);
    }
}

void func_foo()
{
    unsigned int data;
     
    void (*funcPtr) (unsigned int) = fooSink;
    data = 0;
     
    data = UINT_MAX;
     
    funcPtr(data);
}



 
