#include <stdio.h>

long long factorial1(int n){
    long long fact=1;
    if(n-1>0)
        fact=n*factorial1(n-1);
    else
        return fact;
}
long long factorial2(int n){
    long long fact=1;
    for(int i=1;i<=n;i++)
        fact*=i;
    return fact;
}

int main(){

    printf("Input an integer number(1 - 35): ");
    int n;
    scanf("%d", &n);

    while(n<0){
        printf("Enter nonnegative number:");
        scanf("%d",&n);
    }

    long long fact1=factorial1(n);

    long long fact2=factorial2(n);


    printf("%d! = %lld\n", n, fact1);
    printf("%d! = %lld\n", n, fact2);

}
