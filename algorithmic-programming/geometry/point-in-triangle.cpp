#include <iostream>

using namespace std;

double s(double x1,double y1,double x2, double y2,double x3,double y3){
    return abs((x2-x1)*(y3-y1)-(x3-x1)*(y2-y1))/2;
}

int main()
{
    double x1,y1,x2,y2,x3,y3,x0,y0;
    cin>>x1>>y1>>x2>>y2>>x3>>y3>>x0>>y0;
    double s123=s(x1,y1,x2,y2,x3,y3);
    double s120=s(x1,y1,x2,y2,x0,y0);
    double s103=s(x1,y1,x0,y0,x3,y3);
    double s023=s(x0,y0,x2,y2,x3,y3);
    if(s123==s120+s103+s023){
        if(s023==0 || s103==0 || s120==0)
            cout <<"On";
        else
            cout <<"In";
    }
    else{
        cout <<"Out";
    }
    return 0;
}
