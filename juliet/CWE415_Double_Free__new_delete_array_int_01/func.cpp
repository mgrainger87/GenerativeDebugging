 
 

#include "std_testcase.h"

#include <wchar.h>

namespace func
{


void foo()
{
    int * data;
     
    data = NULL;
    data = new int[100];
     
    delete [] data;
     
    delete [] data;
}



}  

 

