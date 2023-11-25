 
 

#include "std_testcase.h"


 
static int fooStatic = 0;

static void fooSink(unsigned int data)
{
    if(fooStatic)
    {
        if(data > 0)  
        {
             
            unsigned int result = data * 2;
            printUnsignedLine(result);
        }
    }
}

void func_foo()
{
    unsigned int data;
    data = 0;
     
    data = UINT_MAX;
    fooStatic = 1;  
    fooSink(data);
}



 

