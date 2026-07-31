#include <iostream>

using namespace std;

int n,m,a[100000];

int findRight(int x){
    int l=0,r=n-1;
    while(l<r){
        int m=(l+r+1)/2;
        if(a[m]<=x){
            l=m;
        }else{//a[m]>x
            r=m-1;
        }
    }
    if(a[r]!=x)
        return -1;
    else
        return r;
}
int findLeft(int x){
    int l=0,r=n-1;
    while(l<r){
        int m=(l+r)/2;
        if(a[m]>=x){
            r=m;
        }else{//a[m]<x
            l=m+1;
        }
    }
    if(a[r]!=x)
        return -1;
    else
        return l;
}

int main()
{
    cin>>n;
    for(int i =0;i<n;i++){
        cin>>a[i];
    }
    cin>>m;
    for(int i =0;i<m;i++){
        int x;
        cin>>x;
        int l1=findLeft(x);
        int r1=findRight(x);
        if(l1==-1){
            cout<<0<<endl;
        }else
            cout<<r1-l1+1<<endl;
    }
    return 0;
}
