#include <iostream>

using namespace std;

int main()
{
    string s;
    cin>>s;
    int nk1=0, nk2=0;
    for(int i=0;i<s.length();i++){
        if(s[i]=='k'){
            nk2++;
            if(nk2>nk1){
                nk1=nk2;
            }
        }
        else{
            nk2=0;
        }
    }
    cout <<nk1<< endl;
    return 0;
}
