 
 

#include "std_testcase.h"

#include <wchar.h>


void func_foo()
{
    char * data;
    char * dataBuffer = (char *)ALLOCA(100*sizeof(char));
    memset(dataBuffer, 'A', 100-1);
    dataBuffer[100-1] = '\0';
    if(1)
    {
         
        data = dataBuffer - 8;
    }
    {
        char dest[100];
        memset(dest, 'C', 100-1);  
        dest[100-1] = '\0';  
         
        memmove(dest, data, 100*sizeof(char));
         
        dest[100-1] = '\0';
        printLine(dest);
    }
}



 

