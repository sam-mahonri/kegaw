class BuiltinManager:
    @staticmethod
    def get_impl(n):
        d={"talk":"char* talk(){char* b=malloc(1024);if(fgets(b,1024,stdin))b[strcspn(b,\"\\n\")]=0;return b;}"}
        return d.get(n)
    @staticmethod
    def resolve(n,args,syms):
        args=[a.strip() for a in args]
        if n=="trans":
            t,v=args[0],args[1]
            return f"atoi({v})" if t=="#int" else f"atof({v})" if t=="#float" else v
        if n=="talk":return "talk()"
        if n=="terminal":return f"system({args[0]})"
        if n=="runc":
            r=args[0]
            if len(r)>=2 and r[0] in ['"',"'"] and r[0]==r[-1]:r=r[1:-1]
            return r.replace('\\"','"').replace("\\'","'")
        if n=="print":
            arg,nl=args[0],"\\n"
            if len(args)>1 and args[1]=="#flow":nl=""
            is_str=arg.startswith('"') or syms.get(arg)=="string"
            return f'printf("{ "%s" if is_str else "%d" }{nl}", {arg});fflush(stdout);'
        return f"{n}({', '.join(args)})"