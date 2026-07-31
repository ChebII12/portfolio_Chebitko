#include <iostream>
#include <algorithm>
#include <stack>
#include <string>
#include <cmath>

using namespace std;

stack<int>st;

int main()
{
    string s;
    int a,b;
    while(cin>>s){
        if(s[0]=='+'){
            a=st.top(); st.pop();
            b=st.top(); st.pop();
            a=a+b;
            st.push(a);
        }else
        if(s[0]=='-'){
            a=st.top(); st.pop();
            b=st.top(); st.pop();
            a=b-a;
            st.push(a);
        }else
        if(s[0]=='*'){
            a=st.top(); st.pop();
            b=st.top(); st.pop();
            a=a*b;
            st.push(a);
        }else
        if(s[0]=='/'){
            a=st.top(); st.pop();
            b=st.top(); st.pop();
            a=b/a;
            st.push(a);
        }else
        {
            int x=stoi(s);
            st.push(x);
        }
    }
    cout<<st.top();
}
