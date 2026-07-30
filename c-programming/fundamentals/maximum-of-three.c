#include <stdio.h>

int main(){
    float a,b,c;
    printf("Enter three numbers:\n");
    scanf(" %f %f %f", &a,&b,&c);
    float max=a;
    (b>max) ? max=b : max;
    (c>max) ?  max=c : max;
    /*
    if(b>max)
        max=b;
    if(c>max)
        max=c;*/
    printf("The maximum of three numbers is %.2f",max);
    return 0;
}
