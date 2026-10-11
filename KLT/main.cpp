// main.cpp : Defines the entry point for the console application.
//

#include <stdio.h>  // printf

extern "C" {
	void RunExample1();
	void RunExample2();
	void RunExample3();
	void RunExample4();
	void RunExample5();
}

int main(int argc, char* argv[])
{
	// select which example to run here
	int which = 0;

	// run the appropriate exampleddddd
	do{
        printf("Ingresa el número de opción en un rango de [1,5]: ");
        int usuario = scanf("%d", &which);
        switch (which) {
            case 1:  RunExample1();  break;
            case 2:  RunExample2();  break;
            case 3:  RunExample3();  break;
            case 4:  RunExample4();  break;  // Note:  example4 reads output from example 3
            case 5:  RunExample5();  break;
            default:  printf("There is no example number %d\n", which);
        }
    }while(which < 1 || which > 5);

	return 0;
}

