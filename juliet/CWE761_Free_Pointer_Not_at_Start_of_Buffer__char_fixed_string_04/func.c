 
 

#include "std_testcase.h"

#include <wchar.h>

#define BAD_SOURCE_FIXED_STRING "Fixed String"  

#define SEARCH_CHAR 'S'

 
static const int STATIC_CONST_TRUE = 1;  
static const int STATIC_CONST_FALSE = 0;  


void func_foo()
{
    char * data;
    data = (char *)malloc(100*sizeof(char));
    if (data == NULL) {exit(-1);}
    data[0] = '\0';
     
    strcpy(data, BAD_SOURCE_FIXED_STRING);
    if(STATIC_CONST_TRUE)
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



 

