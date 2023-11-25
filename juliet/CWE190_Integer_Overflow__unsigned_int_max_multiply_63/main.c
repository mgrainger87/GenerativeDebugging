#include <time.h>
#include <stdlib.h>

	void func_foo();


int main(int argc, char * argv[]) {
	/* seed randomness */
	srand( (unsigned)time(NULL) );
	func_foo();
}
