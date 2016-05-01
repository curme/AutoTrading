 void pop() {
        int x = stack[stack.size()-1];
        stack.pop_back();
        int i = 0;
        for ( ; i < minstack.size(); i++){
            if (minstack[i] == x) break;
        }
        if (i == minstack.size()-1){
            minstack.pop_back();
        }
        else{
            minstack[i] = minstack[minstack.size()-1];
            minstack.pop_back();
            heap(minstack[i], i);
        }
