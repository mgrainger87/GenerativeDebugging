 
 

#include "std_testcase.h"


void func_foo()
{
    int data;
     
    data = -1;
     
    data = -5;
    {
        int buffer[10] = { 0 };
         
        if (data < 10)
        {
            printIntLine(buffer[data]);
        }
        else
        {
            printLine("ERROR: Array index is too big.");
        }
    }
}



 

