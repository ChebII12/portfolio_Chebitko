#include <stdio.h>
#include <stdlib.h>
#include <string.h>
//#include <unistd.h>

#define _CRT_SECURE_NO_WARNINGS

#define MAX_NUMBER_EMPL 20
#define MAX_NAME_LEN 19



struct Person {
    char name[MAX_NAME_LEN+1];
    int age;
    float salary;
};

void load(struct Person arr[MAX_NUMBER_EMPL], int* k) {
    FILE *f = fopen("./file.txt", "r+");
    if (f == NULL) {
        printf("Error opening file!\n");
        *k=0;
        return ;
    }
    fscanf(f, "%d ", k);
    for (int i = 0; i <*k; i++)
        fscanf(f, " %[^,],%d,%f" , arr[i].name, &arr[i].age,  &arr[i].salary);

    fclose(f);
}

void save(struct Person arr[MAX_NUMBER_EMPL], int* k) {
    FILE *f = fopen("./file.txt", "w");

    if (f == NULL) {
        printf("Error opening file for writing!\n");
        return;
    }

    fprintf(f, "%d\n", *k);
    for (int i = 0; i < *k; i++)
        fprintf(f, " %s, %d, %10.2f\n", arr[i].name, arr[i].age, arr[i].salary);

    fclose(f);
}


void clearBuf() {
    int c;
    while ((c = getchar()) != '\n' && c != EOF);
}

void printPerson(struct Person p) {
    printf ("Name: %20s | Age: %3d | Salary: %10.2f \n", p.name, p.age, p.salary) ;
}

void addPerson(struct Person arr[MAX_NUMBER_EMPL], int* k) {
    if (*k >= MAX_NUMBER_EMPL) {
        printf("Your array is full\n");
    }
    else {
        //printf("Warning: If you enter a name longer than %d characters, any characters after %d will not be read.\n", MAX_NAME_LEN, MAX_NAME_LEN);
        printf("Enter name (up to %d characters) : \n", MAX_NAME_LEN);
        char temp[100];
        //int s;
        while((scanf(" %[^\n]s", temp))!=1 || strlen(temp)>MAX_NAME_LEN+1) {
            clearBuf();
            printf("Invalid input, try again\n");
        }
        //printf("s=%d\n", s);
        strcpy(arr[*k].name, temp);
        clearBuf();

        printf("Enter age : \n");
        while(scanf(" %d", &arr[*k].age)!=1 || arr[*k].age < 0) {
            clearBuf();
            printf("Invalid input, try again\n");
        }
        clearBuf();

        printf("Enter salary : \n");
        while(scanf(" %f", &arr[*k].salary)!=1 || arr[*k].salary < 0) {
            clearBuf();
            printf("Invalid input, try again\n");
        }
        clearBuf();
        (*k)++;
    }
}

void printEmployees(struct Person arr[MAX_NUMBER_EMPL], int k) {
    if(k==0) {
        printf("Your list is empty");
        return;
    }
    for (int i = 0; i < k; i++) {
        printPerson(arr[i]);
    }
    printf("\n");
}

int main (){

    /*char cwd[1024];
    if (getcwd(cwd, sizeof(cwd)) != NULL) {
        printf("Current working directory: %s\n", cwd);
    } else {
        perror("getcwd() error");
        return 1;
    }*/

    int emplCount=0;
    struct Person employees[MAX_NUMBER_EMPL];
    int choice=1;
    load(employees, &emplCount);
    while(choice) {
        printf("Enter 1 - to add employee, 2 - to print list of employees, 3 - to save in file, 0 - to exit\n");
        while (scanf("%d", &choice)!=1 || choice > 3 || choice < 0 ) {
            clearBuf();
            printf("Invalid input, try again\n");
        }
        switch (choice) {
            case 1:
                addPerson(employees, &emplCount);
                printf("\n");
                break;
            case 2:
                printEmployees(employees, emplCount);
                printf("\n");
                clearBuf();
                getchar();
                break;
            case 3:
                save(employees, &emplCount);
                printf("\n");
                break;
            case 0:
                printf("End of program\n");
                break;
            default:
                printf("Invalid choice\n");
                break;
        }
        system("cls");
    }
    return 0;
}
