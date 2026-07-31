#include <bits/stdc++.h>

using namespace std;

map<string,int>m;
map<string,int>::iterator iter;

int main()
{
    int n;
    cin>>n;
    for(int i=0;i<n;i++){
        string s;
        cin>>s;
        m[s]++;
    }
    int mx=0;
    string res;
    for(iter=m.begin(); iter!=m.end();iter++)
        if(iter->second >= mx){
        mx=iter->second;
        res=iter->first;
        }
    cout<<res<<" "<<mx;
}
