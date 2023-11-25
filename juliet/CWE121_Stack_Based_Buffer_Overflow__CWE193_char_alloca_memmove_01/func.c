 
 

#include "std_testcase.h"

#include <wchar.h>

 
#define SRC_STRING "AAAAAAAAAA"


void func_foo()
{
    char * data;
    char * dataBadBuffer = (char *)ALLOCA((10)*sizeof(char));
    char * dataGoodBuffer = (char *)ALLOCA((10+1)*sizeof(char));
     
    data = dataBadBuffer;
    data[0] = '\0';  
    {
        char source[10+1] = SRC_STRING;
         
         
        memmove(data, source, (strlen(source) + 1) * sizeof(char));
        printLine(data);
    }
}



 

