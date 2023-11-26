 
 

#include "std_testcase.h"

#include <wchar.h>


void func_foo()
{
    char * data;
    char dataBuffer[100];
    data = dataBuffer;
     
    memset(data, 'A', 100-1);  
    data[100-1] = '\0';  
    {
        char dest[50] = "";
         
        memmove(dest, data, strlen(data)*sizeof(char));
        dest[50-1] = '\0';  
        printLine(data);
    }
}



 

