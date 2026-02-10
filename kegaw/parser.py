import re
from .error import ErrorHandler
class Parser:
    def __init__(self, syntax, aka):
        self.s,self.aka=syntax,{v:k for k,v in aka.items()}
    def parse_args(self,s):
        if not s or not s.strip():return []
        return [x.strip() for x in re.findall(r'("(?:\\.|[^"])*"|[^,]+)',s) if x.strip()]
    def _map(self,n):return self.aka.get(n,n)
    def analyze_line(self,ld):
        ln,cnt=ld
        t,p,term="UNKNOWN",{},self.s['SENTENCE_END']
        cl=cnt.strip()
        if cl.endswith(term):cl=cl[:-len(term)].strip()
        fs,as1,ae,ss=self.s['FUNC_START'],self.s['ARGS_START'],self.s['ARGS_END'],self.s['SCOPE_START']
        if cl.startswith("@use"):
            tgt=cl.replace("@use","").strip()
            if tgt.startswith("^"):tgt="^"+self._map(tgt[1:])
            t,p="IMPORT",{"target":tgt}
        elif self.s['ASSIGN'] in cl:
            tgt,expr=cl.split(self.s['ASSIGN'],1)
            if fs in expr and as1 in expr:
                fn=self._map(expr.split(as1)[0].replace(fs,"").strip())
                p,t={"target":tgt.strip(),"call":{"name":fn,"args":self.parse_args(expr[expr.find(as1)+len(as1):expr.rfind(ae)])}},"ASSIGN_CALL"
            else:p,t={"target":tgt.strip(),"expr":expr.strip()},"ASSIGN"
        elif cl.startswith(fs):
            if cl.endswith(ss):
                h=cl.replace(fs,"",1).replace(ss,"")
                fn=self._map(h.split(as1)[0].strip() if as1 in h else h.strip())
                ra=h[h.find(as1)+len(as1):h.rfind(ae)] if as1 in h else ""
                if fn=="depends":t,p="IF_BLOCK",{"condition":ra}
                elif fn=="while":t,p="WHILE_BLOCK",{"condition":ra}
                else:t,p="FUNC_DEF",{"name":fn,"args":self.parse_args(ra)}
            elif as1 in cl and ae in cl:
                c=cl.replace(fs,"",1)
                fn=self._map(c.split(as1)[0].strip())
                p,t={"name":fn,"args":self.parse_args(c[c.find(as1)+len(as1):c.rfind(ae)])},"FUNC_CALL"
            elif "#" in cl:
                cmd=cl.split("#")[0].replace(fs,"").strip()
                if self._map(cmd)=="drawer":
                    d=cl.split("#",1)[1].strip().split()
                    if len(d)>=2:p,t={"declaration":f"{'char*' if d[0]=='string' else d[0]} {d[1]}"},"VAR_DECL"
        elif cl==self.s['SCOPE_END']:t="SCOPE_CLOSE"
        elif cl.startswith("return"):t,p="RETURN",{"expr":cl.replace("return","").strip()}
        return {"type":t,"payload":p,"line":ln}