 
 

#include "std_testcase.h"

 
static const int STATIC_CONST_TRUE = 1;  
static const int STATIC_CONST_FALSE = 0;  


void func_foo()
{
    unsigned int data;
    data = 0;
    if(STATIC_CONST_TRUE)
    {
         
        data = UINT_MAX;
    }
    if(STATIC_CONST_TRUE)
    {
        {
             
            unsigned int result = data + 1;
            printUnsignedLine(result);
        }
    }
}



 

