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
    sort(a,a+n);
    for(int k=0;k<n-2;k++){
        int i=k+1,j=n-1;
        while(i<j){
            if(a[i]+a[j]<x-a[k])i++;
            else if (a[i]+a[j]>x-a[k]) j--;
            else{
                cout<<a[k]<<' '<<a[i]<<' '<<a[j];
                exit(0);
            }
        }
    }
    cout<<-1;
}
