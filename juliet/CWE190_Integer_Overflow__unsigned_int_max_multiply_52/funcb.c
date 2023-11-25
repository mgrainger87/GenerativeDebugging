 
 

#include "std_testcase.h"


 
void funcc_fooSink(unsigned int data);

void funcb_fooSink(unsigned int data)
{
    funcc_fooSink(data);
}


