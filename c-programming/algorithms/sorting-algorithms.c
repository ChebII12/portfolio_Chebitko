#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void selectionSortAsc(int arr[], int n);
void insertionSortAsc(int arr[], int n);
void bubbleSortAsc(int arr[], int n);
void clearBuf();
int* duplicateArray(int arr[], int n);
void printArray(int arr[], int n);
void swap(int* a, int* b);
int findMin(int* arr, int a, int b);
void randomArray(int arr[], int n, int min, int max);

int main(void) {
    int n=0;
    printf("Enter the number of elements: ");
    while(scanf("%d", &n)!=1 || n<1) {
        printf("Please enter a  decimal number large than 1 .\n");
        clearBuf();
    }

    int* arr = (int*)malloc(n*sizeof(int));

    /*printf("Enter the decimal elements: ");
    for (int i = 0; i < n; i++)
        scanf("%d", &arr[i]);
    clearBuf();*/

    int min, max;
    printf("Enter the minimum and maximum value: ");
    while(scanf("%d%d", &min, &max)!=2 || min>max) {
        printf("Please enter correct values.\n");
    }
    clearBuf();

    randomArray(arr, n, min, max);

    int* dup1=duplicateArray(arr, n);
    int* dup2=duplicateArray(arr, n);
    int* dup3=duplicateArray(arr, n);

    clock_t t1 = clock();
    selectionSortAsc(dup1, n);
    clock_t t2 = clock();
    insertionSortAsc(dup2, n);
    clock_t t3 = clock();
    bubbleSortAsc(dup3, n);
    clock_t t4 = clock();

    printf("Original array: \n");
    printArray(arr, n);

    printf("Result of selection sort:\n");
    printArray(dup1, n);
    printf("Time: %.50f\n", (double)(t2-t1)/CLOCKS_PER_SEC);

    printf("\nResult of insertion sort:\n");
    printArray(dup2, n);
    printf("Time: %.50f\n", (double)(t3-t2)/CLOCKS_PER_SEC);

    printf("\nResult of bubble sort:\n");
    printArray(dup3, n);
    printf("Time: %.50f\n", (double)(t4-t3)/CLOCKS_PER_SEC);

    getchar();getchar();

    free(dup1); free(dup2); free(dup3);
    free(arr);
    return 0;
}

void bubbleSortAsc(int arr[], int n) {
    for (int i = 0; i < n-1; i++)
        for (int j = 0; j < n-i-1; j++)
            if (arr[j] > arr[j+1])
                swap(&arr[j], &arr[j+1]);
}

void selectionSortAsc(int arr[], int n) {
    int k=0;
    for (int i = 0; i < n; i++) {
        k=findMin(arr, i, n);
        swap(&arr[i], &arr[k]);
    }
}

void insertionSortAsc(int arr[], int n) {
    for (int i = 1; i < n; i++)
        for (int j = 0; j < i; j++)
            if (arr[i] < arr[j] )
                for (int k = i; k >j; k--)
                    swap(&arr[k], &arr[k-1]);

}

int* duplicateArray(int arr[], int n) {
    int* dupArr = (int*)malloc(n*sizeof(int));
    for (int i = 0; i < n; i++)
        dupArr[i] = arr[i];
    return dupArr;

}

void printArray(int arr[], int n) {
    for (int i = 0; i < n; i++)
        printf("%4d ", arr[i]);
    printf("\n");
}

void swap(int* a, int* b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

int findMin(int* arr, int a, int b) {
    int min = arr[a];
    int k=a;
    for (int i = a+1; i < b; i++)
        if (arr[i] < min) {
            min = arr[i];
            k=i;
        }
    return k;
}

void clearBuf() {
    int c;
    while ((c = getchar()) != '\n' && c != EOF);
}

void randomArray(int arr[], int n, int min, int max) {
    srand(time(0));
    for (int i = 0; i < n; i++)
        arr[i] = rand()%(max-min+1)+min;
}