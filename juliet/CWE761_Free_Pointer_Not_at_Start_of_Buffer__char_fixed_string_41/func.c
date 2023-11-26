 
 

#include "std_testcase.h"

#include <wchar.h>

#define BAD_SOURCE_FIXED_STRING "Fixed String"  

#define SEARCH_CHAR 'S'


static void fooSink(char * data)
{
     
    for (; *data != '\0'; data++)
    {
        if (*data == SEARCH_CHAR)
        {
            printLine("We have a match!");
            break;
        }
    }
    free(data);
}

void func_foo()
{
    char * data;
    data = (char *)malloc(100*sizeof(char));
    if (data == NULL) {exit(-1);}
    data[0] = '\0';
     
    strcpy(data, BAD_SOURCE_FIXED_STRING);
    fooSink(data);
}



 

