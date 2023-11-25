 
 

#include "std_testcase.h"


void func_foo()
{
    if(1)
    {
        {
            int *intPointer = NULL;
            intPointer = (int *)malloc(sizeof(int));
            *intPointer = 5;
            printIntLine(*intPointer);
             
            if (intPointer != NULL)
            {
                *intPointer = 10;
            }
            printIntLine(*intPointer);
        }
    }
}



 

