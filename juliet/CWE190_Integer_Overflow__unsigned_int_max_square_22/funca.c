 
 

#include "std_testcase.h"


 
int func_fooGlobal = 0;

void func_fooSink(unsigned int data);

void func_foo()
{
    unsigned int data;
    data = 0;
     
    data = UINT_MAX;
    func_fooGlobal = 1;  
    func_fooSink(data);
}



 

