#include <stdio.h>
#include <math.h>

#define PI 3.14159265

int main(){
    float deg, rad;
    printf("Enter the angle value in degrees: ");
    scanf("%f", &deg);
    unsigned short op;
    printf("Select operation 1-sin(x) 2-cos(x) 3-tan(x) 4-cot(x): ");
    scanf("%d", &op);
    rad=deg*PI/180;
    if((op==3 && fabs(sin(rad))<0.015) || (op==4 && fabs(cos(rad))<0.015)){
        printf("Does not exist!");
        return 0;
    }
    switch (op){
        case 1: printf("sin(%.3f deg)=%.4f\n", deg, sin(rad));
            break;
        case 2: printf("cos(%.3f deg)=%.4f\n", deg, cos(rad));
            break;
        case 3: printf("tan(%.3f deg)=%.4f\n", tan(rad));
            break;
        case 4: printf("cot(%.3f deg)=%.4f\n",1/tan(rad));
            break;
        default: printf("No such operation!");
    }

    return 0;
}
