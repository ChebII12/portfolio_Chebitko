#include <iostream>

using namespace std;

/*int fac(int a){
    int factorial=1;
    for(int i = 1; i <= a; ++i) {
        factorial *= i;
    }
    return factorial;
}
int n(int j){
    int nd=0;
    for(int i=1;i<=j;i++){
        if(j%i==0) nd++;
    }
    return fac(nd+3-1)/(fac(3)*fac(nd-1))
}*/

int main()
{
    int k,nd,sum=0;
    cin>>k;
    for(int a=1;a<=k;a++){
        for(int b=1;b<=k/a;b++){
            for(int c=1;c<=k/(a*b);c++){
                if(a*b*c<=k) sum++;
            }
        }
    }
    cout <<sum<< endl;
    return 0;
}
