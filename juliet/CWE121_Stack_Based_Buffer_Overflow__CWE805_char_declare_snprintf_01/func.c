 
 

#include "std_testcase.h"

#include <wchar.h>

#define SNPRINTF snprintf


void func_foo()
{
    char * data;
    char dataBadBuffer[50];
    char dataGoodBuffer[100];
     
    data = dataBadBuffer;
    data[0] = '\0';  
    {
        char source[100];
        memset(source, 'C', 100-1);  
        source[100-1] = '\0';  
         
        SNPRINTF(data, 100, "%s", source);
        printLine(data);
    }
}



 

