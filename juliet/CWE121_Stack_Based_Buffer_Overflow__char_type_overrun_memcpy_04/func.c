 
 

#include "std_testcase.h"

#include <wchar.h>

 
#define SRC_STR "0123456789abcdef0123456789abcde"

typedef struct _charVoid
{
    char charFirst[16];
    void * voidSecond;
    void * voidThird;
} charVoid;

 
static const int STATIC_CONST_TRUE = 1;  
static const int STATIC_CONST_FALSE = 0;  


void func_foo()
{
    if(STATIC_CONST_TRUE)
    {
        {
            charVoid structCharVoid;
            structCharVoid.voidSecond = (void *)SRC_STR;
             
            printLine((char *)structCharVoid.voidSecond);
             
            memcpy(structCharVoid.charFirst, SRC_STR, sizeof(structCharVoid));
            structCharVoid.charFirst[(sizeof(structCharVoid.charFirst)/sizeof(char))-1] = '\0';  
            printLine((char *)structCharVoid.charFirst);
            printLine((char *)structCharVoid.voidSecond);
        }
    }
}



 

