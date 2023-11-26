#include <time.h>
#include <stdlib.h>

	namespace CWE121_Stack_Based_Buffer_Overflow__placement_new_alloca_01 { void bad();}


int main(int argc, char * argv[]) {
	/* seed randomness */
	srand( (unsigned)time(NULL) );
	func::foo();
}
