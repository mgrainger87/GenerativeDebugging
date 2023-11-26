 
 

#include "std_testcase.h"

#include <wchar.h>


void func_foo()
{
    char * data;
    char * dataBuffer = (char *)ALLOCA(100*sizeof(char));
    data = dataBuffer;
     
    memset(data, 'A', 100-1);  
    data[100-1] = '\0';  
    {
        char dest[50] = "";
        size_t i, dataLen;
        dataLen = strlen(data);
         
        for (i = 0; i < dataLen; i++)
        {
            dest[i] = data[i];
        }
        dest[50-1] = '\0';  
        printLine(data);
    }
}



 

