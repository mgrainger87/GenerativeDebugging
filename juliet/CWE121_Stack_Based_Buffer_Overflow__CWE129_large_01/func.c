 
 

#include "std_testcase.h"


void func_foo()
{
    int data;
     
    data = -1;
     
    data = 10;
    {
        int i;
        int buffer[10] = { 0 };
         
        if (data >= 0)
        {
            buffer[data] = 1;
             
            for(i = 0; i < 10; i++)
            {
                printIntLine(buffer[i]);
            }
        }
        else
        {
            printLine("ERROR: Array index is negative.");
        }
    }
}



 

