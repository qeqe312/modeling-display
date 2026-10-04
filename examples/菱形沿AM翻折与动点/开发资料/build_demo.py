"""Build the offline folding example using its own retained sources."""
from pathlib import Path
import shutil
import sys
from uuid import uuid4
DEV=Path(__file__).resolve().parent
ROOT=DEV.parents[2]
TITLE='菱形沿AM翻折与动点'
sys.path.insert(0,str(ROOT/'scripts'))
from assemble_demo import assemble
from package_demo import build
def main():
    output=DEV.parent/'成品'
    output.mkdir(parents=True,exist_ok=True)
    working=DEV/(TITLE+'.html')
    assemble(DEV/'源码',TITLE,working,scripts=['model.js','engine.js'])
    directory=DEV/('.build-'+uuid4().hex)
    directory.mkdir()
    try:
        packaged=directory/'inline'
        build(working,packaged,inline=True)
        shutil.copy2(DEV/'使用说明.md',packaged/'使用说明.md')
        for file in packaged.iterdir():shutil.copy2(file,output/file.name)
    finally:
        if directory.resolve().parent!=DEV.resolve():raise ValueError('Unexpected build directory')
        shutil.rmtree(directory)
    print(output/(TITLE+'.html'))
if __name__=='__main__':main()
