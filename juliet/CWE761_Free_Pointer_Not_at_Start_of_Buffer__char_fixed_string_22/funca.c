 
 

#include "std_testcase.h"

#include <wchar.h>

#define BAD_SOURCE_FIXED_STRING "Fixed String"  


 
int func_fooGlobal = 0;

void func_fooSink(char * data);

void func_foo()
{
    char * data;
    data = (char *)malloc(100*sizeof(char));
    if (data == NULL) {exit(-1);}
    data[0] = '\0';
     
    strcpy(data, BAD_SOURCE_FIXED_STRING);
    func_fooGlobal = 1;  
    func_fooSink(data);
}



 

