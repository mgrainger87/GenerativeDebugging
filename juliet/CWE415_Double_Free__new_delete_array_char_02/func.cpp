 
 

#include "std_testcase.h"

#include <wchar.h>

namespace func
{


void foo()
{
    char * data;
     
    data = NULL;
    if(1)
    {
        data = new char[100];
         
        delete [] data;
    }
    if(1)
    {
         
        delete [] data;
    }
}



}  

 

