 
 

#include "std_testcase.h"


void func_foo()
{
    twoIntsStruct * data;
    twoIntsStruct dataBadBuffer[50];
    twoIntsStruct dataGoodBuffer[100];
     
    data = dataBadBuffer;
    {
        twoIntsStruct source[100];
        {
            size_t i;
             
            for (i = 0; i < 100; i++)
            {
                source[i].intOne = 0;
                source[i].intTwo = 0;
            }
        }
         
        memmove(data, source, 100*sizeof(twoIntsStruct));
        printStructLine(&data[0]);
    }
}



 

