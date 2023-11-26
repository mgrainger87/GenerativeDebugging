 
 

#include "std_testcase.h"


void func_foo()
{
    goto sink;
sink:
    {
         
        int *intPointer = NULL;
        if (intPointer == NULL)
        {
            printIntLine(*intPointer);
        }
    }
}



 

