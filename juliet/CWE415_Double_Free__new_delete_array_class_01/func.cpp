 
 

#include "std_testcase.h"

#include <wchar.h>

namespace func
{


void foo()
{
    TwoIntsClass * data;
     
    data = NULL;
    data = new TwoIntsClass[100];
     
    delete [] data;
     
    delete [] data;
}



}  

 

