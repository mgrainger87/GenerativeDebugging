 
 

#include "std_testcase.h"

#include <wchar.h>


void func_foo()
{
    int64_t * data;
     
    data = NULL;
    data = (int64_t *)malloc(100*sizeof(int64_t));
    if (data == NULL) {exit(-1);}
     
    free(data);
     
    free(data);
}



 

