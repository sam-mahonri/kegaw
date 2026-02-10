import os
from .error import ErrorHandler
class ConfigLoader:
    D={"syntax":{"SCOPE_START":":","SCOPE_END":";","ARGS_START":"<","ARGS_END":">","SENTENCE_END":".","ASSIGN":"<-","FUNC_START":"@","COMMENT":"~~~"},"paths":{"SHARDS_PATH":"shards","BUILD_PATH":"build"},"aka":{"print":"log", "drawer":"var"}}
    @staticmethod
    def load(root,sec):
        fp=root/"kegaw.kako"
        if not fp.exists():return ConfigLoader.D.get(sec,{})
        try:
            with open(fp,'r') as f:cnt=f.read()
            if f"@{sec}@" not in cnt:return ConfigLoader.D.get(sec,{})
            s_cnt=cnt.split(f"@{sec}@")[1].split(f"@/{sec}@")[0]
            return {l.split()[0]:l.split()[1].replace("'","").replace('"',"").strip() for l in s_cnt.splitlines() if len(l.split())>=2}
        except:return ConfigLoader.D.get(sec,{})
    @staticmethod
    def validate_syntax(s):
        for r in ['SCOPE_START','SCOPE_END','ARGS_START','ARGS_END','FUNC_START','ASSIGN','SENTENCE_END']:
            if r not in s or not s[r]:ErrorHandler.fatal(f"Missing syntax: {r}")