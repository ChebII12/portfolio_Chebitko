#include<stdio.h>
#include<string.h>
#include<ctype.h>

#define N 50

int main(void) {
    char s1[N]="", s2[N]="", s1_copy[N]="", s1_copy_k[N]="", s3[N]="", sn[N]="";
    unsigned int k=0, t=0, n1=0, n2=0;
    //1
    fputs("Enter first string : ", stdout);
    fgets(s1, N, stdin);

    fputs("Enter second string: ", stdout);
    fgets(s2, N, stdin);

    printf("Enter number: ");
    scanf("%d", &k);

    //2
    unsigned int len1=strlen(s1)-1;
    unsigned int len2=strlen(s2)-1;

   if ( s1[len1] == '\n')
        s1[len1] = '\0';
    if ( s2[len2] == '\n')
        s2[len2] = '\0';

    len1=strlen(s1);
    len2=strlen(s2);
    printf("len1: %d\n len2: %d\n", len1, len2);
    //3
    strcpy(s1_copy, s1);
    fputs("Copy of first string: ", stdout);
    puts(s1_copy);
    //4
    strncpy(s1_copy_k, s1, k);
    printf("Copy of %d elements of first string: ", k);
    puts(s1_copy_k);
    //5
    strcat(s3, s1);
    strcat(s3, s2);
    fputs("Concatenation : ", stdout);
    puts(s3);
    //6
    for (int i=0; i<len1+len2; i++)
        if(isdigit(s3[i])) {
            t=1;
            break;
        }
    if(t)
        printf("This string contains numbers\n");
    else
        printf("This string does not contain numbers\n");
    //7
    printf("Enter two numbers: ");
    scanf("%d %d", &n1,&n2);

    if(n1>n2) {
        unsigned int temp=n1;
        n1=n2;
        n2=temp;
    }

    for (int i=0; i<n2-n1; i++) {
        sn[i]=s3[n1+i-1];
    }
    sn[n2-n1]='\0';
    fputs("String between given numbers : ", stdout);
    puts(sn);

    return 0;
}
