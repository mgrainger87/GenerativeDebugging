#include <time.h>
#include <stdlib.h>

	namespace CWE415_Double_Free__new_delete_array_long_01 { void bad();}


int main(int argc, char * argv[]) {
	/* seed randomness */
	srand( (unsigned)time(NULL) );
	func::foo();
}
