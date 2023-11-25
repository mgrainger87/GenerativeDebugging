 
 

#include "std_testcase.h"

#include <math.h>

namespace func
{


 
void fooSource(unsigned int &data);

void foo()
{
    unsigned int data;
    data = 0;
    fooSource(data);
    {
         
        unsigned int result = data * data;
        printUnsignedLine(result);
    }
}



}  

 

