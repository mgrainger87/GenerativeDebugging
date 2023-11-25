 
 

#include "std_testcase.h"


 
unsigned int funcb_fooSource(unsigned int data);

void func_foo()
{
    unsigned int data;
    data = 0;
    data = funcb_fooSource(data);
    {
         
        unsigned int result = data + 1;
        printUnsignedLine(result);
    }
}



 

