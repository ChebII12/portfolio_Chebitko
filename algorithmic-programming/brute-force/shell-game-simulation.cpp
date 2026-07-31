#include <iostream>

using namespace std;

int main()
{
    int n;
    cin>>n;
    int a[n],b[n],g[n];
    for(int i=0;i<n;i++){
        cin>>a[i]>>b[i]>>g[i];
        a[i]--,b[i]--,g[i]--;
    }
    int res=0;
    for(int i=0;i<3;i++){
        int sh[3]={0,0,0}, cnt=0;
        sh[i]=1;
        for(int j=0;j<n;j++){
            swap(sh[a[j]], sh[b[j]]);
            cnt+=sh[g[j]];
        }
        res=max(cnt,res);
    }
    cout<<res;
}
