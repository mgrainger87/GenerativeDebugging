 
 

#include "std_testcase.h"


void func_foo()
{
    {
        twoIntsStruct *twoIntsStructPointer = NULL;
         
        if ((twoIntsStructPointer != NULL) & (twoIntsStructPointer->intOne == 5))
        {
            printLine("intOne == 5");
        }
    }
}



 

