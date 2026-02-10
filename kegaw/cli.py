import sys,os,argparse,subprocess
from pathlib import Path
from .config import ConfigLoader
from .lexer import Lexer
from .parser import Parser
from .codegen.engine import CodeGenerator
from .builder.compiler import Builder
from .error import ErrorHandler
def main():
    print(f"\033[38;5;208mKegaw Lang - Compiler - v1.0.1\033[0m")
    print(f"\033[38;5;93m(c) 2026 - Sam Mahonri aka Zhyrel - Apache License Version 2.0\033[0m")
    p=argparse.ArgumentParser(description="Kegaw Compiler")
    p.add_argument("src",help="Project root directory")
    p.add_argument("-o","--output",help="Output binary name",default="app")
    p.add_argument("--keepc",action="store_true",help="Keep generated C/H files")
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
    lex,parse,links,generated_files=Lexer(syntax),Parser(syntax,aka),[],[]
    if shards_dir.exists():
        for s in shards_dir.rglob("*.kako"):
            sid="#".join(s.relative_to(shards_dir).with_suffix('').parts)
            ast=[parse.analyze_line(l) for l in lex.process_file(s)]
            gen=CodeGenerator()
            c_code=gen.generate(ast)
            h_lines=[f"int {n['payload']['name']}({gen._make_sig(n['payload']['args'])});" for n in ast if n['type']=="FUNC_DEF"]
            c_path,h_path=build_dir/f"{sid}.c",build_dir/f"{sid}.h"
            with open(c_path,'w') as f:f.write(c_code)
            with open(h_path,'w') as f:f.write("\n".join(h_lines))
            links.append(str(c_path))
            generated_files.extend([c_path,h_path])
    main_keg=root/"main.keg"
    if not main_keg.exists():ErrorHandler.fatal("main.keg not found")
    ast_m=[parse.analyze_line(l) for l in lex.process_file(main_keg)]
    main_c_path=build_dir/"main.c"
    with open(main_c_path,'w') as f:f.write(CodeGenerator().generate(ast_m,True))
    links.append(str(main_c_path))
    generated_files.append(main_c_path)
    out_name=args.output+(".exe" if sys.platform=="win32" else "")
    bin_path=build_dir/out_name
    Builder.compile(links,bin_path)
    if not args.keepc:
        for f in generated_files:
            if f.exists():f.unlink()
        ErrorHandler.info("Intermediate C files removed | use --keepc to keep C source")
    ErrorHandler.success(f"Successfully compiled: {bin_path}")
if __name__=="__main__":main()