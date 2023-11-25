 
 

#include "std_testcase.h"


void func_foo()
{
    unsigned int data;
    data = 0;
    if(globalTrue)
    {
         
        data = UINT_MAX;
    }
    if(globalTrue)
    {
        if(data > 0)  
        {
             
            unsigned int result = data * 2;
            printUnsignedLine(result);
        }
    }
}



 

