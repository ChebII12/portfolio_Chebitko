#include <iostream>

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
    int n,s,k,sum=0;
    cin>>n>>s>>k;
    make_set(s);
    for(int i=1;i<=n;i++){
        make_set(i);
    }
    for(int i=0;i<k;i++){
        int a,b;
        cin>>a>>b;
        Union(a,b);
    }
    for(int i=1;i<=n;i++){
        if(Repr(i)!=Repr(s))
            sum++;
    }
    cout<<sum;

}
