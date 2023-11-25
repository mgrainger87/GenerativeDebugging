 

#include "std_testcase.h"

namespace func
{


class BadClass 
{
    public:
        BadClass(const char *data)
        {
            if (data) 
            {
                this->data = new char[strlen(data) + 1];
                strcpy(this->data, data);
            } 
            else 
            {
                this->data = new char[1];
                *(this->data) = '\0';
            }
        }

        ~BadClass()
        {
            delete [] data;
        }

        void printData()
        {
            printLine(data);
        }

        BadClass(BadClass &fooClassObject)
        { 
            this->data = new char[strlen(fooClassObject.data) + 1];
            strcpy(this->data, fooClassObject.data); 
        }

    private:
        char *data;
};

void foo()
{
    BadClass fooClassObject1("One"), fooClassObject2("Two");

     
    fooClassObject2 = fooClassObject1;

    fooClassObject2.printData();
}


}  

  

