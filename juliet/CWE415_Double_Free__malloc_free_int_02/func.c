 
 

#include "std_testcase.h"

#include <wchar.h>


void func_foo()
{
    int * data;
     
    data = NULL;
    if(1)
    {
        data = (int *)malloc(100*sizeof(int));
        if (data == NULL) {exit(-1);}
         
        free(data);
    }
    if(1)
    {
         
        free(data);
    }
}



 

