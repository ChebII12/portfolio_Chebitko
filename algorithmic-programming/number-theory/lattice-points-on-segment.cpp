#include <bits/stdc++.h>
#include <cmath>

using namespace std;


int main()
{
    long long x1,x2,y1,y2;
    cin>>x1>>y1>>x2>>y2;
    cout <<1+__gcd(abs(x2-x1),abs(y2-y1))<< endl;
    return 0;
}
