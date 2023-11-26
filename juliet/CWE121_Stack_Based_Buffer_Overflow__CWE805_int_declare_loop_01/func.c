 
 

#include "std_testcase.h"


void func_foo()
{
    int * data;
    int dataBadBuffer[50];
    int dataGoodBuffer[100];
     
    data = dataBadBuffer;
    {
        int source[100] = {0};  
        {
            size_t i;
             
            for (i = 0; i < 100; i++)
            {
                data[i] = source[i];
            }
            printIntLine(data[0]);
        }
    }
}



 

