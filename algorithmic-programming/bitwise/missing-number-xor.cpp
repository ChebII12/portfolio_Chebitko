#include <bits/stdc++.h>

using namespace std;

int main(){

    int n;
    cin>>n;
    int r=0;
    for(int i=0; i<n-1; i++){
        int x;
        cin>>x;
        r^=x;
    }

    int t=0;
    for(int i=1; i<= n; i++)
        t^=i;
    r=r^t;
    cout<<r;
}
