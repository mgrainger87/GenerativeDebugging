 
 

#include "std_testcase.h"


void func_foo()
{
    int * data;
    data = NULL;
     
    data = (int *)ALLOCA(10);
    {
        int source[10] = {0};
         
        memcpy(data, source, 10*sizeof(int));
        printIntLine(data[0]);
    }
}



 

