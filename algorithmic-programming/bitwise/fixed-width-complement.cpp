#include <iostream>

using namespace std;

int main()
{
    int q;
    cin>>q;
    while(q--){
        long long x,n;
        cin>>n;
        x=n;
        int k=0;
        while(x!=0){
            k++;
            x>>=1;
        }
        long long sh=(1LL<<k)-1;
        n=(~n)&sh;
        cout<<n<<'\n';
    }
}
