#include <bits/stdc++.h>

using namespace std;
const double PI=acos(-1.0);

int main()
{
    double x1,x2,r1,r2,y1,y2;
    cin>>x1>>y1>>r1>>x2>>y2>>r2;
    double d=hypot(x2-x1,y2-y1);
    if(d>=r1+r2){
        cout<<"0\n";
        return 0;
    }
    if(d+r1<=r2){
        cout<<PI*r1*r1<<"\n";
        return 0;
    }
    if(d+r2<=r1){
        cout<<PI*r2*r2<<"\n";
        return 0;
    }
    double a1=acos((r1*r1+d*d-r2*r2)/(2*r1*d));
    double a2=acos((r2*r2+d*d-r1*r1)/(2*r2*d));
    cout<<(a1-sin(2*a1)/2)*r1*r1+(a2-sin(2*a2)/2)*r2*r2<<'\n';
}
