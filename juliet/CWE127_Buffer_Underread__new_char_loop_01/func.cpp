 
 

#include "std_testcase.h"

#include <wchar.h>

namespace func
{


void foo()
{
    char * data;
    data = NULL;
    {
        char * dataBuffer = new char[100];
        memset(dataBuffer, 'A', 100-1);
        dataBuffer[100-1] = '\0';
         
        data = dataBuffer - 8;
    }
    {
        size_t i;
        char dest[100];
        memset(dest, 'C', 100-1);  
        dest[100-1] = '\0';  
         
        for (i = 0; i < 100; i++)
        {
            dest[i] = data[i];
        }
         
        dest[100-1] = '\0';
        printLine(dest);
         
    }
}



}  

 

