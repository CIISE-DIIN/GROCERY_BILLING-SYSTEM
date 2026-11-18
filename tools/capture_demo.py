"""Capture an actual CLI session in a pseudoterminal and render excerpts."""
import os
import pty
import select
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]

def capture():
    with tempfile.TemporaryDirectory() as folder:
        master, slave = pty.openpty()
        proc = subprocess.Popen([sys.executable, '-u', str(ROOT / 'main.py'), '--data-file', str(Path(folder) / 'demo.json')],
                                stdin=slave, stdout=slave, stderr=slave)
        os.close(slave)
        # The terminal echoes these keystrokes, preserving the inputs as evidence.
        inputs = [('Choose an option: ', '1'), ('Choose an option: ', '2'),
                  ('Product code: ', 'P001'), ('Quantity (whole units): ', '4'),
                  ('Choose an option: ', '2'), ('Product code: ', 'P002'),
                  ('Quantity (whole units): ', '2'), ('Choose an option: ', '3'),
                  ('Choose an option: ', '6'), ('Cash received in RM (or C to cancel): ', '100'),
                  ('Choose an option: ', '6'), ('Cash received in RM (or C to cancel): ', '150'),
                  ('Choose an option: ', '7'), ('Receipt ID to view (Enter to return): ', 'GBS-00001'),
                  ('Choose an option: ', '0')]
        transcript, pending, index = '', '', 0
        while True:
            ready, _, _ = select.select([master], [], [], 5)
            if not ready:
                proc.kill()
                raise RuntimeError('Demo timed out')
            try:
                chunk = os.read(master, 65536).decode()
            except OSError:
                break
            if not chunk:
                break
            transcript += chunk
            pending += chunk
            if index < len(inputs) and inputs[index][0] in pending:
                prompt, answer = inputs[index]
                pending = pending.split(prompt, 1)[1]
                os.write(master, (answer + '\n').encode())
                index += 1
        os.close(master)
        if proc.wait() != 0:
            raise RuntimeError('Demo failed')
        return transcript.replace('\r\n', '\n')


def render(text, path, label):
    candidates = ['/System/Library/Fonts/Menlo.ttc', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 'C:/Windows/Fonts/consola.ttf']
    font_path = next((p for p in candidates if Path(p).exists()), None)
    font = ImageFont.truetype(font_path, 20) if font_path else ImageFont.load_default()
    lines = text.strip().splitlines()
    width = max(850, int(max(font.getlength(line) for line in lines)) + 64)
    image = Image.new('RGB', (width, len(lines) * 30 + 96), '#111827')
    draw = ImageDraw.Draw(image)
    draw.text((28, 20), label, font=font, fill='#93c5fd')
    for index, line in enumerate(lines):
        draw.text((28, 66 + index * 30), line, font=font, fill='#f3f4f6')
    image.save(path)


def main():
    out = ROOT / 'docs'
    images = out / 'screenshots'
    images.mkdir(parents=True, exist_ok=True)
    transcript = capture()
    (out / 'demo_transcript.txt').write_text(transcript)
    menu = transcript[transcript.index('============================================'):transcript.index('Choose an option: ') + len('Choose an option: 1')]
    catalogue = transcript[transcript.index('PRODUCT CATALOGUE'):transcript.index('\n============================================', transcript.index('PRODUCT CATALOGUE'))]
    error_line = next(line for line in transcript.splitlines() if line.startswith('ERROR:'))
    receipt_start = transcript.index('ISSE GROCERY BILLING SYSTEM\nRECEIPT')
    receipt = transcript[receipt_start:transcript.index('Sale saved. Cart cleared.', receipt_start) + len('Sale saved. Cart cleared.')]
    render(menu, images / '01_menu.png', 'Captured application session | main menu')
    render(catalogue, images / '02_catalogue.png', 'Captured application session | product catalogue')
    render('Cash received in RM (or C to cancel): 100\n' + error_line, images / '03_validation.png', 'Captured application session | rejected payment')
    render(receipt, images / '04_receipt.png', 'Captured application session | successful checkout')
    tests = (out / 'test_results.txt').read_text()
    render(tests[tests.index('----------------------------------------------------------------------'):], images / '05_tests.png', 'Actual automated test summary')
    print('Captured session and five evidence images.')

if __name__ == '__main__':
    main()
