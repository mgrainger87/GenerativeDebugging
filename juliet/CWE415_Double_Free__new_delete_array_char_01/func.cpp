 
 

#include "std_testcase.h"

#include <wchar.h>

namespace func
{


void foo()
{
    char * data;
     
    data = NULL;
    data = new char[100];
     
    delete [] data;
     
    delete [] data;
}



}  

 

