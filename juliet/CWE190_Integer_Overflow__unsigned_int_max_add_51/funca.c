 
 

#include "std_testcase.h"


 
void funcb_fooSink(unsigned int data);

void func_foo()
{
    unsigned int data;
    data = 0;
     
    data = UINT_MAX;
    funcb_fooSink(data);
}



 

