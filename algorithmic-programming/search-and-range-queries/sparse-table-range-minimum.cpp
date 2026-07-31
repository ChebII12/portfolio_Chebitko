/*#include <iostream>

using namespace std;

#define L1 100010
#define L2 17
int m[L1][L2];
int a[L1], b[L1];
int mas[L1][L2];
int n;

void Build_RMQ_Array(int *b)
{
    int i, j;
    for (i = 1; i <= n; i++) mas[i][0] = b[i];
    for (j = 1; 1 << j <= n; j++)
        for (i = 1; i + (1 << j) - 1 <= n; i++)
        if (mas[i][j - 1] > mas[i + (1 << (j - 1))][j - 1])
            mas[i][j] = mas[i][j - 1];
        else mas[i][j] = mas[i + (1 << (j - 1))][j - 1];
}

int RMQ(int i, int j){
    int k = 0;
    while ((1 << (k + 1)) <= j - i + 1) k++;
    return min(mas[i][k],mas[j - (1<<k) + 1][k]);

}

int main()
{
    int n,q;
    cin>>n>>q;
    for(int i = 1; i <= n; i++)
        cin>>b[i];
    for(int i = 1; i <= n; i++)
        a[b[i]] = i;
    Build_RMQ_Array(a);
    for(int i = 0; i < q; i++){
        int u,v;
        cin>>u>>v;
        cout<<RMQ(u,v);

    }
}*/
#include <iostream>
#include <algorithm>
#include <vector>

using namespace std;

#define L1 100010
#define L2 17

int mas[L1][L2];

void Build_RMQ_Array(int *b, int n)
{
    int i, j;
    for (i = 1; i <= n; i++) mas[i][0] = b[i];
    for (j = 1; 1 << j <= n; j++)
        for (i = 1; i + (1 << j) - 1 <= n; i++)
            mas[i][j] = min(mas[i][j - 1], mas[i + (1 << (j - 1))][j - 1]);
}

int RMQ(int i, int j)
{
    int k = 0;
    while ((1 << (k + 1)) <= j - i + 1) k++;
    return min(mas[i][k], mas[j - (1 << k) + 1][k]);
}

int main()
{
    int n, q;
    cin >> n >> q;
    int b[L1], a[L1];
    for (int i = 1; i <= n; i++)
    {
        cin >> b[i];
        a[b[i]] = i;
    }
    Build_RMQ_Array(a, n);
    for (int i = 0; i < q; i++)
    {
        int u, v;
        cin >> u >> v;
        cout << RMQ(u, v) << endl;
    }
    return 0;
}
