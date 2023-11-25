 
 

#include "std_testcase.h"


void func_foo()
{
    int64_t * data;
    int64_t dataBadBuffer[50];
    int64_t dataGoodBuffer[100];
     
    data = dataBadBuffer;
    {
        int64_t source[100] = {0};  
        {
            size_t i;
             
            for (i = 0; i < 100; i++)
            {
                data[i] = source[i];
            }
            printLongLongLine(data[0]);
        }
    }
}



 

