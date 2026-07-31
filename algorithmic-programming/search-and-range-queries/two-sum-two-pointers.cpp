#include <bits/stdc++.h>

using namespace std;

int main()
{
    ios_base::sync_with_stdio(false);cin.tie(NULL);
    int n,x;
    cin>>n>>x;
    int a[n];
    for(int i=0;i<n;i++){
        cin>>a[i];
    }
    int i=0,j=n-1;
    while(i<j){
        if(a[i]+a[j]<x)i++;
        else if (a[i]+a[j]>x) j--;
        else{
            cout<<"YES";
            exit(0);
        }
    }
    cout<<"NO";
}
