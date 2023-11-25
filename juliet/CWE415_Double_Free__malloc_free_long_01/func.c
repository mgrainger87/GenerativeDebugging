 
 

#include "std_testcase.h"

#include <wchar.h>


void func_foo()
{
    long * data;
     
    data = NULL;
    data = (long *)malloc(100*sizeof(long));
    if (data == NULL) {exit(-1);}
     
    free(data);
     
    free(data);
}



 

