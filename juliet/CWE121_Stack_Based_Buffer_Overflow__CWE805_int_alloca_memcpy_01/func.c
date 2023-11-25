 
 

#include "std_testcase.h"


void func_foo()
{
    int * data;
    int * dataBadBuffer = (int *)ALLOCA(50*sizeof(int));
    int * dataGoodBuffer = (int *)ALLOCA(100*sizeof(int));
     
    data = dataBadBuffer;
    {
        int source[100] = {0};  
         
        memcpy(data, source, 100*sizeof(int));
        printIntLine(data[0]);
    }
}



 

