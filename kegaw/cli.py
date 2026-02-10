import sys,os,argparse,subprocess
from pathlib import Path
from .config import ConfigLoader
from .lexer import Lexer
from .parser import Parser
from .codegen.engine import CodeGenerator
from .builder.compiler import Builder
from .error import ErrorHandler
def main():
    p=argparse.ArgumentParser(description="Kegaw Compiler")
    p.add_argument("src",help="Project root directory")
    p.add_argument("-o","--output",help="Output binary name",default="app")
    args=p.parse_args()
    cc=Builder.get_cc()
    try:
        subprocess.run([cc,"--version"],capture_output=True)
    except:
        ErrorHandler.fatal(f"C Compiler ({cc}) not found. Please install GCC or MinGW.")
    root=Path(args.src).resolve()
    if not root.exists():ErrorHandler.fatal(f"Directory not found: {root}")
    ErrorHandler.info(f"Building project at: {root}")
    syntax,paths,aka=ConfigLoader.load(root,"syntax"),ConfigLoader.load(root,"paths"),ConfigLoader.load(root,"aka")
    ConfigLoader.validate_syntax(syntax)
    build_dir,shards_dir=root/paths.get('BUILD_PATH','build'),root/paths.get('SHARDS_PATH','shards')
    if not build_dir.exists():build_dir.mkdir()
    lex,parse,links=Lexer(syntax),Parser(syntax,aka),[]
    if shards_dir.exists():
        for s in shards_dir.rglob("*.kako"):
            sid="#".join(s.relative_to(shards_dir).with_suffix('').parts)
            ast=[parse.analyze_line(l) for l in lex.process_file(s)]
            gen=CodeGenerator()
            c_code=gen.generate(ast)
            h_lines=[f"int {n['payload']['name']}({gen._make_sig(n['payload']['args'])});" for n in ast if n['type']=="FUNC_DEF"]
            with open(build_dir/f"{sid}.c",'w') as f:f.write(c_code)
            with open(build_dir/f"{sid}.h",'w') as f:f.write("\n".join(h_lines))
            links.append(str(build_dir/f"{sid}.c"))
    main_keg=root/"main.keg"
    if not main_keg.exists():ErrorHandler.fatal("main.keg not found")
    ast_m=[parse.analyze_line(l) for l in lex.process_file(main_keg)]
    with open(build_dir/"main.c",'w') as f:f.write(CodeGenerator().generate(ast_m,True))
    links.append(str(build_dir/"main.c"))
    out_name=args.output+(".exe" if sys.platform=="win32" else "")
    bin_path=build_dir/out_name
    Builder.compile(links,bin_path)
    ErrorHandler.success(f"Successfully compiled: {bin_path}")
if __name__=="__main__":main()