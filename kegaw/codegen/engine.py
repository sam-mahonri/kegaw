from .builtins import BuiltinManager
class CodeGenerator:
    def __init__(self):
        self.headers,self.proto,self.body,self.built,self.syms,self.scps=["#include <stdio.h>","#include <stdlib.h>","#include <string.h>","#include <unistd.h>"],[],[],set(),{},[]
        self.heap_vars,self.last_was_return=[],False
    def _make_sig(self,args):
        r=[]
        for a in args:
            p=a.split()
            if len(p)==2:r.append(f"{'char*' if p[0]=='string' else p[0]} {p[1]}")
            else:r.append(f"int {a}")
        return ", ".join(r)
    def emit(self,c,i):self.body.append(f"{'    '*i}{c}")
    def _inject_cleanup(self,ind,exc=None):
        for v in self.heap_vars:
            if v!=exc:self.emit(f"if({v}) {{free({v}); {v}=NULL;}}",ind)
    def generate(self,ast,is_main=False):
        ind=0
        for n in ast:
            if n['type']=="FUNC_DEF" and not (n['payload']['name']=='a' and is_main):
                self.proto.append(f"int {n['payload']['name']}({self._make_sig(n['payload']['args'])});")
        for n in ast:
            t,p=n['type'],n['payload']
            if t=="IMPORT":
                tgt=p['target']
                if tgt.startswith("^"):
                    impl=BuiltinManager.get_impl(tgt[1:])
                    if impl:self.built.add(impl)
                else:self.headers.append(f'#include "{tgt}.h"')
            elif t=="VAR_DECL":
                d,v=p['declaration'],p['declaration'].split()[1]
                if p['declaration'].startswith("char*"):
                    self.syms[v],self.last_was_return="string",False
                    self.heap_vars.append(v)
                    self.emit(f"char* {v}=NULL;",ind)
                else:self.syms[v],self.last_was_return="int",False;self.emit(f"{d};",ind)
            elif t=="ASSIGN":self.emit(f"{p['target']} = {p['expr']};",ind);self.last_was_return=False
            elif t=="ASSIGN_CALL":
                tgt=p['target']
                if self.syms.get(tgt)=="string":self.emit(f"if({tgt}) free({tgt});",ind)
                self.emit(f"{tgt} = {BuiltinManager.resolve(p['call']['name'],p['call']['args'],self.syms)};",ind)
                self.last_was_return=False
            elif t=="FUNC_DEF":
                self.heap_vars,self.last_was_return=[],False
                for a in p['args']:
                    ap=a.split()
                    self.syms[ap[1] if len(ap)==2 else a]="string" if (len(ap)==2 and ap[0]=="string") else "int"
                self.scps.append("FUNC")
                line="int main() {" if (p['name']=='a' and is_main) else f"int {p['name']}({self._make_sig(p['args'])}) {{"
                self.emit(line,ind);ind+=1
            elif t in ["IF_BLOCK","WHILE_BLOCK"]:self.scps.append("BLOCK");self.emit(f"{'if' if t=='IF_BLOCK' else 'while'} ({p['condition']}) {{",ind);ind+=1;self.last_was_return=False
            elif t=="SCOPE_CLOSE":
                ind=max(0,ind-1)
                if self.scps and self.scps.pop()=="FUNC":
                    self._inject_cleanup(ind+1)
                    if not self.last_was_return:self.emit("return 0;",ind+1)
                self.emit("}",ind);self.last_was_return=False
            elif t=="RETURN":
                val=p['expr'].strip()
                self._inject_cleanup(ind,exc=val);self.emit(f"return {val};",ind);self.last_was_return=True
            elif t=="FUNC_CALL":
                res=BuiltinManager.resolve(p['name'],p['args'],self.syms)
                if p['name']=="talk":self.emit(f"free({res});",ind)
                else:self.emit(res if res.endswith(";") or "fflush" in res else f"{res};",ind)
                self.last_was_return=False
        return f"{chr(10).join(self.headers)}\n\n{chr(10).join(self.proto)}\n\n{chr(10).join(self.built)}\n\n{chr(10).join(self.body)}"