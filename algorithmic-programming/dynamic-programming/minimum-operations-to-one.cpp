#include <iostream>

using namespace std;

long long  a[1000001];

int main()
{
    int n;
    a[1]=0;
    for(int i=2;i<=1000000;i++){
        a[i]=a[i-1]+1;
        if(i%3==0 && a[i]>a[i/3]+1) a[i]=a[i/3]+1;
        if(i%2==0 && a[i]>a[i/2]+1) a[i]=a[i/2]+1;
    }
    while(cin>>n){
        cout<<a[n]<<"\n";
    }
}
