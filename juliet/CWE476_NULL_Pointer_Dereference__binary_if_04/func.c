 
 

#include "std_testcase.h"

 
static const int STATIC_CONST_TRUE = 1;  
static const int STATIC_CONST_FALSE = 0;  


void func_foo()
{
    if(STATIC_CONST_TRUE)
    {
        {
            twoIntsStruct *twoIntsStructPointer = NULL;
             
            if ((twoIntsStructPointer != NULL) & (twoIntsStructPointer->intOne == 5))
            {
                printLine("intOne == 5");
            }
        }
    }
}



 

