 
 

#include "std_testcase.h"


void func_foo()
{
    if(1)
    {
        {
             
            int *intPointer = NULL;
            if (intPointer == NULL)
            {
                printIntLine(*intPointer);
            }
        }
    }
}



 

