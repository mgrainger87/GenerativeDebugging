 
 

#include "std_testcase.h"


void func_foo()
{
    int * data;
    int dataBadBuffer[50];
    int dataGoodBuffer[100];
     
    data = dataBadBuffer;
    {
        int source[100] = {0};  
         
        memmove(data, source, 100*sizeof(int));
        printIntLine(data[0]);
    }
}



 

