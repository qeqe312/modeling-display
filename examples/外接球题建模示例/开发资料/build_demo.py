"""Rebuild the retained full-solution demo directly from its own source."""
from pathlib import Path
import re
import shutil
import sys
import tempfile

DEV = Path(__file__).resolve().parent
ROOT = DEV.parents[2]
SOURCE = DEV / '源码'
TITLE = '外接球题建模示例'
sys.path.insert(0, str(ROOT / 'scripts'))
from package_demo import build


def assemble():
    template = (ROOT / 'assets' / 'template.html').read_text(encoding='utf-8')
    css = (SOURCE / 'style.css').read_text(encoding='utf-8')
    layout = (SOURCE / 'layout.html').read_text(encoding='utf-8')
    script = (SOURCE / 'app.js').read_text(encoding='utf-8')
    template = re.sub(r'<!--\s*=+.*?-->', '<!-- Modeling-display full solution variant: cached geometry, approved settings, all proof content visible. -->', template, count=1, flags=re.S)
    template = template.replace('__TITLE__', TITLE)
    template = template.replace('width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover', 'width=device-width,initial-scale=1,viewport-fit=cover')
    start = template.index('<style>')
    end = template.index('</style>', start) + len('</style>')
    template = template[:start] + '<style>\n' + css + '\n</style>' + template[end:]
    start = template.index('<body>') + len('<body>')
    end = template.index('<!-- THREE_DEPENDENCY_START -->', start)
    template = template[:start] + '\n' + layout + '\n' + template[end:]
    start = template.index('<script>', template.index('<!-- THREE_DEPENDENCY_END -->'))
    end = template.index('</script>', start) + len('</script>')
    template = template[:start] + '<script>\n' + script + '\n</script>' + template[end:]
    page = SOURCE / (TITLE + '.html')
    page.write_text(template, encoding='utf-8')
    return page


def main():
    output = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEV.parent / '成品'
    if output == SOURCE.resolve() or output.is_relative_to(SOURCE.resolve()):
        raise ValueError('Output must be separate from the retained source')
    output.mkdir(parents=True, exist_ok=True)
    page = assemble()
    # All temporary packaging work stays under the checked development directory.
    with tempfile.TemporaryDirectory(prefix='.build-', dir=DEV) as directory:
        temp = Path(directory).resolve()
        if not temp.is_relative_to(DEV.resolve()):
            raise ValueError('Temporary directory is outside the intended workspace')
        build(page, temp / 'inline', True)
        build(page, temp / 'offline', False)
        readme = (DEV / '使用说明.md').read_bytes()
        for name in ('inline', 'offline'):
            (temp / name / '使用说明.md').write_bytes(readme)
        for file in (temp / 'inline').iterdir():
            shutil.copy2(file, output / file.name)
        offline = output / '离线双文件版'
        offline.mkdir(exist_ok=True)
        for file in (temp / 'offline').iterdir():
            shutil.copy2(file, offline / file.name)
    print(output / (TITLE + '.html'))


if __name__ == '__main__':
    main()
