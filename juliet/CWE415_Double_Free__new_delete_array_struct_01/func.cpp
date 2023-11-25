 
 

#include "std_testcase.h"

#include <wchar.h>

namespace func
{


void foo()
{
    twoIntsStruct * data;
     
    data = NULL;
    data = new twoIntsStruct[100];
     
    delete [] data;
     
    delete [] data;
}



}  

 

