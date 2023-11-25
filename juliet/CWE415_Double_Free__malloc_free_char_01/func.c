 
 

#include "std_testcase.h"

#include <wchar.h>


void func_foo()
{
    char * data;
     
    data = NULL;
    data = (char *)malloc(100*sizeof(char));
    if (data == NULL) {exit(-1);}
     
    free(data);
     
    free(data);
}



 

