 
 

#include "std_testcase.h"

#include <math.h>


 
void funcc_fooSink(unsigned int data);

void funcb_fooSink(unsigned int data)
{
    funcc_fooSink(data);
}

