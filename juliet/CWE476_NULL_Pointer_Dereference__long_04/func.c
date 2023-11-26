 
 

#include "std_testcase.h"

#include <wchar.h>

 
static const int STATIC_CONST_TRUE = 1;  
static const int STATIC_CONST_FALSE = 0;  


void func_foo()
{
    long * data;
    if(STATIC_CONST_TRUE)
    {
         
        data = NULL;
    }
    if(STATIC_CONST_TRUE)
    {
         
        printLongLine(*data);
    }
}



 

