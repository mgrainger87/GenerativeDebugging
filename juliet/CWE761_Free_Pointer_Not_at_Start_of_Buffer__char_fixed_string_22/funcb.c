 
 

#include "std_testcase.h"

#include <wchar.h>

#define SEARCH_CHAR 'S'


 
extern int func_fooGlobal;

void func_fooSink(char * data)
{
    if(func_fooGlobal)
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
}


