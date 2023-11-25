 
 

#include "std_testcase.h"

#include <math.h>

typedef union
{
    unsigned int unionFirst;
    unsigned int unionSecond;
} func_unionType;


void func_foo()
{
    unsigned int data;
    func_unionType myUnion;
    data = 0;
     
    data = UINT_MAX;
    myUnion.unionFirst = data;
    {
        unsigned int data = myUnion.unionSecond;
        {
             
            unsigned int result = data * data;
            printUnsignedLine(result);
        }
    }
}



 
