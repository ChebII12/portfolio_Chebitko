/*#include <iostream>
#include <algorithm>

using namespace std;

int main()
{
    int n;
    cin>>n;
    int y[n+1];
    for(int i=1;i<=n;i++){
        cin>>y[i];
    }
    int f[n+1];
    f[1]=0;
    f[2]=abs(y[1]-y[2]);
    for(int i=3;i<=n;i++){
        f[i]=min(f[i-1]+abs(y[i]-y[i-1]),f[i-2]+3*abs(y[i]-y[i-2]));
    }
    cout <<f[n]<< endl;
    return 0;
}*/
#include <bits/stdc++.h>
using namespace std;
int n, h[100001], e[100001], p[100001], res[100001];

int main() {
    cin >> n;
    for (int i=1; i<=n; i++)
        cin >> h[i];

    e[1]=0; p[1]=-1;
    e[2]=abs(h[2]-h[1]); p[2] = 1;

    for (int j=3; j<=n; j++)
        if ((e[j - 1] + abs(h[j] - h[j -1])) < (e[j-2]+3*abs(h[j]-h[j-2]))){
            e[j]=e[j-1]+abs(h[j]-h[j-1]);
            p[j]=j-1;
            }
            else {
                e[j]=e[j-2]+3*abs(h[j]-h[j-2]), p[j] = j-2;
            }

    int ans=0;
    for (int i=n; i>0; i=p[i])
        res[ans++]=i;

    cout <<e[n]<<"\n"<<ans<<"\n";
    for (int i=ans-1; i>=0; i-- )
        cout << res[i] << " ";
}
