#include <time.h>
#include <stdlib.h>

	namespace CWE476_NULL_Pointer_Dereference__class_03 { void bad();}


int main(int argc, char * argv[]) {
	/* seed randomness */
	srand( (unsigned)time(NULL) );
	func::foo();
}
