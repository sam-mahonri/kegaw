from .builtins import BuiltinManager
class CodeGenerator:
    def __init__(self):
        self.headers,self.proto,self.body,self.built,self.syms,self.scps=["#include <stdio.h>","#include <stdlib.h>","#include <string.h>","#include <unistd.h>"],[],[],set(),{},[]
        self.last_was_return = False
    def _make_sig(self,args):
        r=[]
        for a in args:
            p=a.split()
            if len(p)==2:r.append(f"{'char*' if p[0]=='string' else p[0]} {p[1]}")
            else:r.append(f"int {a}")
        return ", ".join(r)
    def emit(self,c,i):self.body.append(f"{'    '*i}{c}")
    def generate(self,ast,is_main=False):
        ind=0
        for n in ast:
            if n['type']=="FUNC_DEF" and not (n['payload']['name']=='a' and is_main):
                self.proto.append(f"int {n['payload']['name']}({self._make_sig(n['payload']['args'])});")
        for n in ast:
            t,p=n['type'],n['payload']
            self.last_was_return = (t == "RETURN")
            if t=="IMPORT":
                tgt=p['target']
                if tgt.startswith("^"):
                    impl=BuiltinManager.get_impl(tgt[1:])
                    if impl:self.built.add(impl)
                else:self.headers.append(f'#include "{tgt}.h"')
            elif t=="VAR_DECL":
                d=p['declaration']
                parts=d.split()
                if len(parts)>=2:self.syms[parts[1]]="string" if parts[0]=="char*" else "int"
                self.emit(f"{d};",ind)
            elif t=="ASSIGN":self.emit(f"{p['target']} = {p['expr']};",ind)
            elif t=="ASSIGN_CALL":self.emit(f"{p['target']} = {BuiltinManager.resolve(p['call']['name'],p['call']['args'],self.syms)};",ind)
            elif t=="FUNC_DEF":
                for a in p['args']:
                    ap=a.split()
                    self.syms[ap[1] if len(ap)==2 else a]="string" if (len(ap)==2 and ap[0]=="string") else "int"
                self.scps.append("FUNC")
                line="int main() {" if (p['name']=='a' and is_main) else f"int {p['name']}({self._make_sig(p['args'])}) {{"
                self.emit(line,ind);ind+=1
            elif t in ["IF_BLOCK","WHILE_BLOCK"]:
                self.scps.append("BLOCK")
                self.emit(f"{'if' if t=='IF_BLOCK' else 'while'} ({p['condition']}) {{",ind);ind+=1
            elif t=="SCOPE_CLOSE":
                ind=max(0,ind-1)
                if self.scps and self.scps.pop()=="FUNC" and not self.last_was_return:self.emit("return 0;",ind+1)
                self.emit("}",ind)
            elif t=="RETURN":self.emit(f"return {p['expr']};",ind)
            elif t=="FUNC_CALL":
                res=BuiltinManager.resolve(p['name'],p['args'],self.syms)
                self.emit(res if res.endswith(";") else f"{res};",ind)
        return f"{chr(10).join(self.headers)}\n\n{chr(10).join(self.proto)}\n\n{chr(10).join(self.built)}\n\n{chr(10).join(self.body)}"