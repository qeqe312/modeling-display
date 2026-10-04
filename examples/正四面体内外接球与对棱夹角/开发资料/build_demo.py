"""Rebuild this example from its own readable sources and verified repository vendor."""
from pathlib import Path
import shutil
import sys
import tempfile

DEV = Path(__file__).resolve().parent
ROOT = DEV.parents[2]
TITLE = '正四面体内外接球与对棱夹角'
sys.path.insert(0, str(ROOT / 'scripts'))
from assemble_demo import assemble
from package_demo import build


def main():
    output = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEV.parent / '成品'
    if output == DEV.resolve() or output.is_relative_to(DEV.resolve()):
        raise ValueError('Output must be separate from retained development files')
    output.mkdir(parents=True, exist_ok=True)
    working = DEV / (TITLE + '.html')
    assemble(DEV / '源码', TITLE, working, scripts=['model.js', 'engine.js'])
    with tempfile.TemporaryDirectory(prefix='.build-', dir=DEV) as directory:
        packaged = Path(directory) / 'inline'
        build(working, packaged, inline=True)
        shutil.copy2(DEV / '使用说明.md', packaged / '使用说明.md')
        for file in packaged.iterdir():
            shutil.copy2(file, output / file.name)
    print(output / (TITLE + '.html'))


if __name__ == '__main__':
    main()
