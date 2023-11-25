 
 

#include "std_testcase.h"

#include <wchar.h>


void func_foo()
{
    twoIntsStruct * data;
     
    data = NULL;
    data = (twoIntsStruct *)malloc(100*sizeof(twoIntsStruct));
    if (data == NULL) {exit(-1);}
     
    free(data);
     
    free(data);
}



 

