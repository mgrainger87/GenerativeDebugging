 
 

#include "std_testcase.h"

#include <wchar.h>

 
#define SRC_STRING "AAAAAAAAAA"


void func_foo()
{
    char * data;
    char dataBadBuffer[10];
    char dataGoodBuffer[10+1];
     
    data = dataBadBuffer;
    data[0] = '\0';  
    {
        char source[10+1] = SRC_STRING;
         
        strcpy(data, source);
        printLine(data);
    }
}



 

