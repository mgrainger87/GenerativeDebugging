 
 

#include "std_testcase.h"

namespace func
{


void foo()
{
    char * data;
    char * dataBadBuffer = (char *)ALLOCA(sizeof(OneIntClass));
    char * dataGoodBuffer = (char *)ALLOCA(sizeof(TwoIntsClass));
     
    data = dataBadBuffer;
    {
         
         
        TwoIntsClass * classTwo = new(data) TwoIntsClass;
         
        classTwo->intOne = 5;
        classTwo->intTwo = 10;  
        printIntLine(classTwo->intOne);
         
    }
}



}  

 

