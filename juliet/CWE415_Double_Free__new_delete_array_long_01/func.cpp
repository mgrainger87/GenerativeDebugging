 
 

#include "std_testcase.h"

#include <wchar.h>

namespace func
{


void foo()
{
    long * data;
     
    data = NULL;
    data = new long[100];
     
    delete [] data;
     
    delete [] data;
}



}  

 

