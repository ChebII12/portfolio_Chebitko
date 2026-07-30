#include <stdio.h>

int main(){
    int a,b,res1,res2,res3, res4, res5;
    printf("Enter integer numbers a and b:");
    scanf("%d %d", &a,&b);
    printf("%d + %d = %d \n", a,b,a+b);
    printf("%d - %d = %d \n", a,b,a-b);
    if(b!=0)
        printf("%d / %d = %.4f \n", a,b,(1.0*a)/b);
    printf("%d * %d = %d \n", a,b,a*b);
    printf("%d %% %d = %d \n", a,b,a%b);
    return 0;
}
