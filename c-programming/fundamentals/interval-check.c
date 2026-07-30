#include <stdio.h>

int main(){
    float a,b,c, t;
    printf("Enter the interval boundaries and an arbitrary number:\n");
    scanf(" %f %f %f", &a,&b,&c);
    if(b<a){
        printf("erorr\n");
        t=b;
        b=a;
        a=t;
        printf("a and b have been switched\n");
    }
    if(c<=b && c>=a)
        printf("%.2f is in the interval [%.2f, %.2f]", c,a,b);
    else
        printf("%.2f is not in the interval [%.2f, %.2f]", c,a,b);

    return 0;
}
