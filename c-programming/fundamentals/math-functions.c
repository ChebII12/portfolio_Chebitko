#include <stdio.h>
#include <math.h>

int main(){
    float a;
    printf("Enter number:");
    scanf("%f", &a);
    printf("The square root of %.3f is %.3f...\n", a, sqrt(a));
    printf(" ceil(%.3f) = %.1f\n", a, ceil(a));
    printf(" floor(%.3f) = %.1f\n", a, floor(a));
    printf(" round(%.3f)  = %.1f\n", a, round(a));
    printf(" fabs(%.3f)  = %.1f\n", a, fabs(a));
    return 0;
}
