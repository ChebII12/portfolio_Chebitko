#include <stdio.h>

int main(){

    printf("Input an integer number(1 - 1000): ");
    int n,sumfor=0, sumwhile=0, sumwocycl=0;
    scanf("%d", &n);

    while(n<0){
        printf("Enter nonnegative number:");
        scanf("%d",&n);
    }

    int n2=n/2;
    for(int i=1; i<=n2; i++)
        sumfor+=2*i;

    int j=2;
    while(j<=n){
        sumwhile+=j;
        j+=2;
    }

    sumwocycl=n2*(n2+1);

    printf("Sum of all even numbers from 1 to %d using for loop: %d\n", n, sumfor);
    printf("Sum of all even numbers from 1 to %d using while loop: %d\n", n, sumwhile);
    printf("Sum of all even numbers from 1 to %d without using loops: %d\n", n, sumwocycl);

}
