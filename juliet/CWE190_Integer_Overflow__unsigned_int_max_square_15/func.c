 
 

#include "std_testcase.h"

#include <math.h>


void func_foo()
{
    unsigned int data;
    data = 0;
    switch(6)
    {
    case 6:
         
        data = UINT_MAX;
        break;
    default:
         
        printLine("Benign, fixed string");
        break;
    }
    switch(7)
    {
    case 7:
    {
         
        unsigned int result = data * data;
        printUnsignedLine(result);
    }
    break;
    default:
         
        printLine("Benign, fixed string");
        break;
    }
}



 

