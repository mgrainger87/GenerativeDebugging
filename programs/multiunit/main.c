#include <stdio.h>
#include "helper.h"

int main() {
	int *ptr = NULL;
	modify_value(ptr);
	printf("Modified value: %d\n", *ptr);
	return 0;
}
