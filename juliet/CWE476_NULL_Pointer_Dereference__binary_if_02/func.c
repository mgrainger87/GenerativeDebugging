 
 

#include "std_testcase.h"


void func_foo()
{
    if(1)
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



 

