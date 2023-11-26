 
 

#include "std_testcase.h"

#include <wchar.h>

#define SNPRINTF snprintf


void func_foo()
{
    char * data;
    char dataBuffer[100];
    data = dataBuffer;
     
    memset(data, 'A', 100-1);  
    data[100-1] = '\0';  
    {
        char dest[50] = "";
         
        SNPRINTF(dest, strlen(data), "%s", data);
        printLine(data);
    }
}



 

