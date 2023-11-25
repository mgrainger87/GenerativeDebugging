 
 

#include "std_testcase.h"


static void fooSink(unsigned int data)
{
    {
         
        unsigned int result = data + 1;
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



 
