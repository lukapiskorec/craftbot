"""Export actual-mesh SVG plans to PNG with an explicitly waited headless browser."""
from pathlib import Path
import subprocess
import tempfile
HERE=Path(__file__).resolve().parent
CHROME=Path('C:/Program Files/Google/Chrome/Application/chrome.exe')
for name in ('32','33','34','route_W1','route_E1','route_N1','route_S1','route_E0'):
    with tempfile.TemporaryDirectory(prefix='craftbot17_plan_') as profile:
        target=HERE/f'plan_v03_{name}.png'
        completed=subprocess.run([str(CHROME),'--headless=new',f'--user-data-dir={profile}',
            '--no-first-run','--hide-scrollbars','--allow-file-access-from-files',
            '--window-size=1300,1000',f'--screenshot={target}',(HERE/f'plan_v03_{name}.html').as_uri()],
            capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60)
        if completed.returncode or not target.exists():raise RuntimeError(completed.stderr)
        print(f'{target.name}: {target.stat().st_size} bytes',flush=True)
