#include <bits/stdc++.h>

using namespace std;

bool prime[300005];
int n,m;

void generatePrimes(){
    memset(prime,true,sizeof(prime));
    prime[0]=0;
    prime[1]=0;
    for(int i=2;i*i<=n;i++){
        if(!prime[i]) continue;
        for(int j=i*i;j<=n;j+=i){
            prime[j]=false;
        }
    }
}


/*int IsPrime(int n)

{

  for(int i = 2; i <= sqrt(n); i++)

    if (n % i == 0) return 0;

  return 1;

}*/
void print(){
    int flag=1;
    for(int i=m;i<=n;++i)
    if(prime[i]){cout<<i<<'\n';flag=0;}
        if(flag) cout<<"Absent\n";
}

int main()
{
    cin>>m>>n;
    generatePrimes();
    print();
}
