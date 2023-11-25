 
 

#include "std_testcase.h"


 
extern int func_fooGlobal;

void func_fooSink(unsigned int data)
{
    if(func_fooGlobal)
    {
        if(data > 0)  
        {
             
            unsigned int result = data * 2;
            printUnsignedLine(result);
        }
    }
}


