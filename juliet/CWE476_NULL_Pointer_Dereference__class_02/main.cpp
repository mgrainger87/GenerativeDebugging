#include <time.h>
#include <stdlib.h>

	namespace func { void foo();}


int main(int argc, char * argv[]) {
	/* seed randomness */
	srand( (unsigned)time(NULL) );
	func::foo();
}
