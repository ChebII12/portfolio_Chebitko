#include <iostream>
#include <algorithm>

using namespace std;

#define L1 500001
int parent[L1];

void make_set(int v)
{
    parent[v] = v;
}

int Repr(int v)
{
    if (v == parent[v]) return v;
    return parent[v] = Repr(parent[v]);
}

void Union(int x, int y)
{
    int x1 = Repr(x), y1 = Repr(y);
    if (x1 == y1) return;
    parent[x1] = y1;
}

int main()
{
    int n,m;
    cin>>n>>m;
    for(int i=0;i<m;i++){
        string x;
        int u,v;
        cin>>x>>u>>v;
        if(parent[u]==0)
            make_set(u);
        if(parent[v]==0)
            make_set(v);
        if(x=="union")

            Union(u,v);
        if(x=="get"){
            if(Repr(u)==Repr(v))
                cout<<"YES\n";
            else
               cout<<"NO\n";
        }

    }

}
