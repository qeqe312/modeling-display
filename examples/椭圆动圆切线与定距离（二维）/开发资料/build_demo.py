"""Build this dependency-free Canvas 2D example from its own retained sources."""
import argparse
from html import escape
from pathlib import Path
import re
import shutil

DEV=Path(__file__).resolve().parent
ROOT=DEV.parents[2]
FILENAME='椭圆动圆切线与定距离.html'
TITLE='椭圆 · 动圆切线与定距离（二维）'

def assemble():
    source=DEV/'源码'
    css=(source/'style.css').read_text(encoding='utf-8')
    layout=(source/'layout.html').read_text(encoding='utf-8')
    script=(source/'app.js').read_text(encoding='utf-8')
    if '</style' in css.lower() or '</script' in script.lower():
        raise ValueError('Source contains a closing tag that would terminate an inline block')
    if re.search(r'<\s*(script|iframe|object|embed)\b|\son\w+\s*=|javascript:',layout,re.I):
        raise ValueError('Unexpected executable markup in layout')
    if re.search(r'@import|url\s*\(|<\s*(link|img|audio|video)\b|\b(?:src|href)\s*=',css+'\n'+layout,re.I):
        raise ValueError('This Canvas example must have no external assets')
    return ('<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '<meta name="color-scheme" content="dark"><title>'+escape(TITLE)+'</title>\n'
            '<style>\n'+css+'\n</style></head><body>\n'+layout+'\n'
            '<script>\n'+script+'\n</script></body></html>\n')

def build(output):
    output=output.resolve()
    if output==DEV or output.is_relative_to(DEV):
        raise ValueError('Delivery directory must be separate from development materials')
    output.mkdir(parents=True,exist_ok=True)
    page=output/FILENAME
    page.write_text(assemble(),encoding='utf-8',newline='\n')
    shutil.copy2(DEV/'使用说明.md',output/'使用说明.md')
    shutil.copy2(ROOT/'LICENSE',output/'LICENSE')
    return page

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=DEV.parent/'成品')
    args=parser.parse_args()
    print(build(args.output))
