"""Verify this example's retained sources, delivery, reports and reference links."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
from zoneinfo import ZoneInfo

DEV = Path(__file__).resolve().parent
BASE = DEV.parent
ROOT = DEV.parents[2]
sys.path.insert(0, str(DEV))
from build_demo import build


def check_archive():
    final = BASE / '成品'
    records = DEV / '验证记录'
    expected = {'椭圆动圆切线与定距离.html', '使用说明.md', 'LICENSE'}
    assert {path.name for path in final.iterdir()} == expected
    with tempfile.TemporaryDirectory(prefix='ellipse-rebuild-') as directory:
        output = Path(directory) / '成品'
        build(output)
        assert all((output / name).read_bytes() == (final / name).read_bytes()
                   for name in expected), 'Rebuilt delivery differs from retained delivery'

    html_hash = hashlib.sha256((final / '椭圆动圆切线与定距离.html').read_bytes()).hexdigest()
    browser = json.loads((records / 'browser-report.json').read_text(encoding='utf-8'))
    inspection = json.loads((records / 'inspection.json').read_text(encoding='utf-8'))
    assert html_hash == browser['metrics']['htmlSHA256'] == inspection['htmlSHA256']
    assert len(inspection['records']) == 32
    for row in inspection['records']:
        assert (records / row['path']).is_file(), row['path']

    docs = [ROOT / 'SKILL.md', ROOT / 'README.md', ROOT / 'examples/README.md',
            ROOT / 'references/example-guide.md', ROOT / 'references/plane-geometry.md',
            BASE / 'REFERENCE.md', DEV / 'README.md']
    links = 0
    for doc in docs:
        for target in re.findall(r'\[[^\]]*\]\(([^)\n]+)\)', doc.read_text(encoding='utf-8')):
            if target.startswith(('http:', 'https:', '#')):
                continue
            path = target.split('#', 1)[0].strip('<>')
            assert (doc.parent / path).exists(), (doc.relative_to(ROOT), path)
            links += 1

    # This is a read-only collection check; it never installs or deploys the skill.
    sys.path.insert(0, str(ROOT / 'scripts'))
    from deploy import collect
    collected = collect(ROOT)
    for path in [BASE / 'REFERENCE.md', DEV / '源码/app.js', DEV / 'build_demo.py',
                 DEV / 'check_archive.py', DEV / '题目/原题.png',
                 ROOT / 'references/plane-geometry.md']:
        assert path.relative_to(ROOT).as_posix() in collected

    report = {
        'date': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
        'htmlSHA256': html_hash,
        'rebuildFromRetainedSourcesIdentical': True,
        'browserAndScreenshotHashesMatch': True,
        'screenshots': len(inspection['records']),
        'localReferenceLinksChecked': links,
        'deploymentCollectorIncludes2DResources': True,
        'actualSkillDeployment': 'not performed by this check',
    }
    (records / 'archive-report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    print(json.dumps(check_archive(), ensure_ascii=True))
