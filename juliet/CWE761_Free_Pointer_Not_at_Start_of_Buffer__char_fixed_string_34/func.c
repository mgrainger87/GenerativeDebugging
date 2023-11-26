 
 

#include "std_testcase.h"

#include <wchar.h>

#define BAD_SOURCE_FIXED_STRING "Fixed String"  

#define SEARCH_CHAR 'S'

typedef union
{
    char * unionFirst;
    char * unionSecond;
} func_unionType;


void func_foo()
{
    char * data;
    func_unionType myUnion;
    data = (char *)malloc(100*sizeof(char));
    if (data == NULL) {exit(-1);}
    data[0] = '\0';
     
    strcpy(data, BAD_SOURCE_FIXED_STRING);
    myUnion.unionFirst = data;
    {
        char * data = myUnion.unionSecond;
         
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



 
