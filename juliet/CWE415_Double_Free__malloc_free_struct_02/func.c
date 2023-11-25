 
 

#include "std_testcase.h"

#include <wchar.h>


void func_foo()
{
    twoIntsStruct * data;
     
    data = NULL;
    if(1)
    {
        data = (twoIntsStruct *)malloc(100*sizeof(twoIntsStruct));
        if (data == NULL) {exit(-1);}
         
        free(data);
    }
    if(1)
    {
         
        free(data);
    }
}



 

