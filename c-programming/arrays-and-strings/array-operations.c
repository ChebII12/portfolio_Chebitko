#include <stdio.h>
#include<stdlib.h>
#include<time.h>

#define N 5
#define M 50
#define RandMax 10000

void printArray (int n, int ar []){
    for (int i = 0; i < n; i++)
        printf("%4d ", ar[i]);
    printf("\n");
}

void scanArray (int n, int ar []){
    for (int i = 0; i < n; i++)
        scanf("%d", &ar[i]);
    printf("\n");
}

int summArray (int n, int ar []){
    int summ=0;
    for (int i = 0; i < n; i++)
        summ+=ar[i];
    return summ;
}

int maxArray (int n, int ar []){
    int max=ar[0];
    for (int i = 1; i < n; i++)
        if(ar[i]>max)
            max=ar[i];
    return max;
}

void fibonacci (int n, int ar []){
    ar[0]=1;
    ar[1]=1;
    for (int i = 2; i < n; i++)
        ar[i]=ar[i-1]+ar[i-2];
}

void random (int n, int ar []){
    srand(time(0));
    for (int i = 0; i < n; i++)
        ar[i]=rand()%RandMax;
}

int main(){

    int arr1[N] = {1, 2, 5, 8};
    int arr2[M], arrf [M], arrR [M];
    int n2, nf, nr;
    // Example
    printf("0. First array \n");
    printArray(N, arr1);

    printf ("First array squared \n") ;
    for (int i=0; i<N; i++)
        arr1[i] = arr1[i]*arr1[i];
    printArray (N, arr1) ;
    printf("\n");

    //Task 1
    printf ("1. Enter the length of the second array 1-%d: \n",M);
    scanf("%d", &n2);
    printf ("n2 = %d\n", n2);

    printf ("Enter the second array: \n");
    scanArray(n2, arr2);

    printf ("Second array \n");
    printArray(n2, arr2);

    //Task 2
    int sumArr2=summArray(n2,arr2);
    printf ("2. The sum of the elements of the second array is %d.\n", sumArr2);
    printf("\n");

    //Task 3
    int maxArr2=maxArray(n2,arr2);
    printf ("3. Max element of the second array is %d.\n", maxArr2);
    printf("\n");

    //Task 4
    printf ("4. Enter the length of Fibonacci array 1-%d: \n",M);
    scanf("%d", &nf);

    fibonacci(nf,arrf);

    printf ("Fibonacci array \n");
    printArray(nf, arrf);
    printf("\n");

    //Task 5
    printf ("5. Enter the length of random array 1-%d: \n",M);
    scanf("%d", &nr);

    random(nr,arrR);

    printf ("Random array \n");
    printArray(nr, arrR);

    return 0;
}
