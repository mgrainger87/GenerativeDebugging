 
 

#include "std_testcase.h"

 
static const int STATIC_CONST_TRUE = 1;  
static const int STATIC_CONST_FALSE = 0;  

namespace func
{


void foo()
{
    TwoIntsClass * data;
    if(STATIC_CONST_TRUE)
    {
         
        data = NULL;
    }
    if(STATIC_CONST_TRUE)
    {
         
        printIntLine(data->intOne);
         
        delete data;
    }
}



}  

 

