 
 

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
        char dest[100*2];
        memset(dest, 'C', 100*2-1);  
        dest[100*2-1] = '\0';  
         
        strcpy(dest, data);
        printLine(dest);
         
    }
}



 

