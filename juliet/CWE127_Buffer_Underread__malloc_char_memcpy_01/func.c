 
 

#include "std_testcase.h"

#include <wchar.h>


void func_foo()
{
    char * data;
    data = NULL;
    {
        char * dataBuffer = (char *)malloc(100*sizeof(char));
        if (dataBuffer == NULL) {exit(-1);}
        memset(dataBuffer, 'A', 100-1);
        dataBuffer[100-1] = '\0';
         
        data = dataBuffer - 8;
    }
    {
        char dest[100];
        memset(dest, 'C', 100-1);  
        dest[100-1] = '\0';  
         
        memcpy(dest, data, 100*sizeof(char));
         
        dest[100-1] = '\0';
        printLine(dest);
         
    }
}



 

