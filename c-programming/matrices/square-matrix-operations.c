#include <stdio.h>
#include<stdlib.h>
#include<time.h>

#define N_ROW 25
#define N_COL 25
#define RandMax 5

void printMatrix (int n, int a[N_ROW][N_COL]){
    for (int i = 0; i < n; i++){
        for (int j = 0; j < n; j++)
            printf("%4d ", a[i][j]);
        printf("\n");
    }
}

void scanMatrix (int n, int a[N_ROW][N_COL]){
    for (int i = 0; i < n; i++){
        printf("Enter %d-th row( %d elements):\n", i+1, n);
        for (int j = 0; j < n; j++){
            scanf("%d", &a[i][j]) ;
        }
    }
    printf("\n");
}
void random (int n, int a[N_ROW][N_COL]){
    srand(time(0));
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            a[i][j]=rand()%RandMax;
}

void sum (int n, int a[N_ROW][N_COL], int b[N_ROW][N_COL], int res[N_ROW][N_COL]){
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            res[i][j]=a[i][j]+b[i][j];
}

void multipl(int n, int a[N_ROW][N_COL], int b[N_ROW][N_COL], int res[N_ROW][N_COL]){
    for (int i = 0; i < n; i++)
        for (int j = 0; j <n; j++){
            res[i][j]=0;
            for (int k = 0; k <n; k++)
                res[i][j]+=a[i][k]*b[k][j];
        }
}

int main (){
    int m1[N_ROW][N_COL], m2[N_ROW][N_COL], mSum[N_ROW][N_COL], mMult1[N_ROW][N_COL]={0}, mMult2[N_ROW][N_COL]={0};
    int n;
    do{
        printf ("Enter size of matrix nxn( one number between 1 and %d):\n", N_COL);
        scanf("%d", &n);
    }while(n<1);

    printf ("Enter your matrix %dx%d\n", n,n);
    scanMatrix(n,m2);

    random(n, m1);
    sum(n, m1, m2, mSum);
    multipl(n, m1, m2, mMult1);
    multipl(n, m2, m1, mMult2);

    //nxm mxk
    printf ("Random matrix A \n");
    printMatrix(n, m1) ;
    printf("Your matrix B \n");
    printMatrix(n, m2) ;
    printf("matrix A+B \n");
    printMatrix(n, mSum) ;
    printf("matrix A*B \n");
    printMatrix(n, mMult1) ;
    printf("matrix B*A \n");
    printMatrix(n, mMult2) ;
    return 0;
}
