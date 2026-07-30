#include <stdio.h>
#define N 100

void transpose(int n, int m1[N][N], int m2[N][N]){
    for(int i=0;i<n;i++)
        for(int j=0; j<n; j++)
            m2[j][i] = m1[i][j];
}


int main(void) {
    int n, m1[N][N], m2[N][N];
    printf("Enter the number of rows and columns of matrix:\n");
    scanf("%d",&n);
    printf("Enter the elements of matrix:\n");
    for(int i=0;i<n;i++)
        for(int j=0;j<n;j++)
            scanf("%d",&m1[i][j]);
    transpose(n,m1,m2);
    printf("Transposed matrix:\n");
    for(int i=0;i<n;i++) {
        for(int j=0;j<n;j++)
            printf("%3d ",m2[i][j]);
        printf("\n");
    }
    return 0;
}
