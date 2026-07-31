#include <bits/stdc++.h>
#include <cmath>

using namespace std;

int main()
{
    long long ch1,z1,ch2,z2,ch3,z3;
    cin>>ch1>>z1>>ch2>>z2;
    z3=abs(z1/__gcd(z1,z2)*z2);
    ch3=ch1*z2/__gcd(z1,z2)+ch2*z1/__gcd(z1,z2);
    cout <<ch3/__gcd(ch3,z3)<<' '<<z3/abs(__gcd(ch3,z3))<< endl;
}
