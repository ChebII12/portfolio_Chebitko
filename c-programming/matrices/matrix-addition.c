#include <stdio.h>
#include<stdlib.h>
#include<time.h>

#define N_ROW 25
#define N_COL 25
#define RandMax 100

void printMatrix (int n, int m, int a[N_ROW][N_COL]){
    for (int i = 0; i < n; i++){
        for (int j = 0; j < m; j++)
            printf("%4d", a[i][j]);
        printf("\n");
    }
    printf("\n");
}

void scanMatrix (int n, int m, int a[N_ROW][N_COL]){
    for (int i = 0; i < n; i++){
        printf("Enter %d-th row( %d elements):\n", i+1, m);
        for (int j = 0; j < m; j++){
            scanf("%d", &a[i][j]) ;
        }
    }
    printf("\n");
}
void random (int n, int m, int a[N_ROW][N_COL]){
    srand(time(0));
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            a[i][j]=rand()%RandMax;
}

void sum (int n, int m, int a[N_ROW][N_COL], int b[N_ROW][N_COL], int res[N_ROW][N_COL]){
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            res[i][j]=a[i][j]+b[i][j];
}

int main (){
    int mRand1[N_ROW][N_COL], m2[N_ROW][N_COL], mSum[N_ROW][N_COL];
    int n,m;
    do{
        printf ("Enter size of matrix( two numbers between 1 and %d):\n", N_COL);
        scanf("%d %d", &n, &m);
    }while(n<1 || m<1);

    printf ("Enter your matrix %dx%d\n", n,m);
    scanMatrix(n,m,m2);

    random(n, m, mRand1);
    sum(n, m, mRand1, m2, mSum);

    printf ("Random matrix A \n");
    printMatrix(n, m, mRand1) ;
    printf("Your matrix B \n");
    printMatrix(n, m, m2) ;
    printf("matrix A+B \n");
    printMatrix(n, m, mSum) ;
    return 0;
}
