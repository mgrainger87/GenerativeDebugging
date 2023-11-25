 
 

#include "std_testcase.h"

#include <wchar.h>

namespace func
{


void foo()
{
    int64_t * data;
     
    data = NULL;
    data = new int64_t[100];
     
    delete [] data;
     
    delete [] data;
}



}  

 

