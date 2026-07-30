#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void clearBuf(){
    int c;
    while ((c = getchar()) != '\n' && c != EOF);
}

void task1(){
    int n;
    float A=0, H=0;
    printf("Enter number of numbers: ");
    while(scanf("%d", &n) != 1 || n < 1 ) {
        clearBuf();
        printf("Invalid input, try again\n");
    }

    float* numb=(float*)malloc(n * sizeof(float));
    if (numb==NULL) {
        printf("Memory allocation error");
        return;
    }

    wrongInput : printf("Enter %d non-zero numbers: ", n);
    for (int i=0; i<n; i++) {
        if(scanf("%f", numb+i)!=1 || *(numb+i)==0) {
            printf("Invalid input, try again\n");
            A=0; H=0;
            clearBuf();
            goto wrongInput;
        }
        // As alternative to goto, we can free memory and call task1() inside if

        A+=*(numb+i);
        H+=(1/(*(numb+i)));
    }

    printf("Arithmetic mean: %.3f\n", A/n);
    printf("Harmonic mean: %.3f\n", n/H);
    free(numb);

}

void task2() {
    int row=0, col=0;
    int rndMax, rndMin;
    srand(time(0));

    printf("Enter number of rows and columns: ");
    while (scanf("%d %d", &row, &col) != 2 || row < 1 || col < 1) {
        clearBuf();
        printf("Invalid input, try again\n");
    }
    clearBuf();

    int* mat = (int*)malloc(row * col * sizeof(int));

    if (mat == NULL) {
        printf("Memory allocation error");
        return;
    }

    printf("Enter two different numbers: ");
    while(scanf(" %d %d", &rndMax, &rndMin)!=2 || rndMax==rndMin) {
        printf("Invalid input, try again\n");
        printf("Enter two different numbers: ");
    }
    if(rndMax<rndMin){
        int temp=rndMax;
        rndMax=rndMin;
        rndMin=temp;
    }

    for (int i = 0; i < row; i++) {
        for (int j = 0; j < col; j++) {
            *(mat+i * col + j) = rndMin+rand()%(rndMax-rndMin+1);
            printf("%4d ", *(mat+i * col + j));
        }
        printf("\n");
    }
    free(mat);
}



int main(void) {
    int choice;

    while(choice) {
        printf("Enter 1 - to run first task (arithmetic and harmonic mean), 2 - to run second task (matrix), 0 - to exit\n");
        while (scanf("%d", &choice)!=1 || choice > 2 || choice < 0 ) {
            clearBuf();
            printf("Invalid input, try again\n");
        }
        switch (choice) {
            case 1:
                task1();
                clearBuf();
                getchar();
            break;
            case 2:
                task2();
                clearBuf();
                getchar();
            break;
            case 0:
                printf("End of program\n");
            break;
            default:
                printf("Invalid choice\n");
            break;
        }
        system("cls");
    }
    return 0;
}
