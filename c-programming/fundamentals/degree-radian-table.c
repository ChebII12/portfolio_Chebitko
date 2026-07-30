#include <stdio.h>

#define PI 3.14159265

int main(){
    printf("|  degrees  |      radians  |\n|===========|===============|\n");
    for(int i=0; i<=360; i+=10){
        if(i==0)
            printf("|  %d        |     %f  |\n|-----------|---------------|\n", i, i*PI/180);
        else if(i<100)
            printf("|  %d      |     %f  |\n|-----------|---------------|\n", i, i*PI/180);
        else
            printf("|  %d      |     %f  |\n|-----------|---------------|\n", i, i*PI/180);
    }

}
