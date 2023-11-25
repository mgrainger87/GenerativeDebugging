 
 

#include "std_testcase.h"


void func_foo()
{
    int64_t * data;
    int64_t * dataBadBuffer = (int64_t *)ALLOCA(50*sizeof(int64_t));
    int64_t * dataGoodBuffer = (int64_t *)ALLOCA(100*sizeof(int64_t));
     
    data = dataBadBuffer;
    {
        int64_t source[100] = {0};  
         
        memcpy(data, source, 100*sizeof(int64_t));
        printLongLongLine(data[0]);
    }
}



 

