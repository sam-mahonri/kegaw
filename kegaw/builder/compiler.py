import subprocess,sys,os
from ..error import ErrorHandler
class Builder:
    @staticmethod
    def get_cc():
        cc="gcc"
        if sys.platform=="win32":
            try:
                r=subprocess.run(["where","gcc"],capture_output=True)
                if r.returncode!=0:cc="mingw32-gcc"
            except:cc="mingw32-gcc"
        return cc
    @staticmethod
    def compile(srcs,out):
        cc=Builder.get_cc()
        cmd=[cc,"-o",str(out)]+srcs
        try:
            r=subprocess.run(cmd,capture_output=True,text=True)
            if r.returncode!=0:ErrorHandler.fatal("C Build error",context=r.stderr)
            return True
        except FileNotFoundError:ErrorHandler.fatal(f"Compiler {cc} not found in system path")
        except Exception as e:ErrorHandler.fatal(f"Unexpected build error: {e}")