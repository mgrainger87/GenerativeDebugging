 
 

#include "std_testcase.h"


 
void funcd_fooSink(unsigned int data);

void funcc_fooSink(unsigned int data)
{
    funcd_fooSink(data);
}


