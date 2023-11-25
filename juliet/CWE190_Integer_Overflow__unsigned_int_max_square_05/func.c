 
 

#include "std_testcase.h"

#include <math.h>

 
static int staticTrue = 1;  
static int staticFalse = 0;  


void func_foo()
{
    unsigned int data;
    data = 0;
    if(staticTrue)
    {
         
        data = UINT_MAX;
    }
    if(staticTrue)
    {
        {
             
            unsigned int result = data * data;
            printUnsignedLine(result);
        }
    }
}



 

