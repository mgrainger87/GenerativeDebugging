 
 

#include "std_testcase.h"

#include <wchar.h>

 
static const int STATIC_CONST_TRUE = 1;  
static const int STATIC_CONST_FALSE = 0;  


void func_foo()
{
    int64_t * data;
    if(STATIC_CONST_TRUE)
    {
         
        data = NULL;
    }
    if(STATIC_CONST_TRUE)
    {
         
        printLongLongLine(*data);
    }
}



 

