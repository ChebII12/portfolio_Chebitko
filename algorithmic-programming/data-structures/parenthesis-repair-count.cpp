/*#include <bits/stdc++.h>
#include <cmath>

using namespace std;

int main()
{
    char s;
    int check=0;
    while((s=getchar())!=EOF){
        if(s=='(')
            check++;
        else if(s==')')
            check--;
        else
            break;
    }
    cout<<abs(check);
}*/
#include <iostream>
#include <stack>

using namespace std;

int main()
{
    string s;
    cin >> s;
    stack<char> st;
    int ans = 0;
    for (int i = 0; i < s.size(); i++)
    {
        if (s[i] == '('){
            st.push(s[i]);
        }
        else if (s[i] == ')'){
            if (st.empty()){
                ans++;
            }
            else{
                st.pop();
            }
        }
    }
    ans += st.size();
    cout << ans << endl;
    return 0;
}
