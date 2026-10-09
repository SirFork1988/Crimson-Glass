#!/usr/bin/env python
"""Rebuild Crimson Glass Plymouth art into this package’s build directory."""
# SPDX-License-Identifier: GPL-2.0-or-later
import argparse
import configparser
import hashlib
import json
import shutil
from pathlib import Path

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QGuiApplication, QImage, QPainter
from PyQt6.QtSvg import QSvgRenderer

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'build/plymouth/crimson-glass'
SCRATCH = ROOT / 'build/plymouth/previews'
SOURCE = Path(__file__).resolve().parent / 'spinner-original'
SHARED_MARK = ROOT / 'sources/art/crimson-mark.svg'
THEME = '''[Plymouth Theme]
Name=Crimson Glass
Description=Charcoal ribbon, crimson animation and a clean Crimson Glass wordmark
ModuleName=two-step

[two-step]
Font=Noto Sans 12
TitleFont=Noto Sans Light 26
MonospaceFont=Noto Sans Mono 12
ImageDir=/usr/share/plymouth/themes/crimson-glass
DialogHorizontalAlignment=.5
DialogVerticalAlignment=.62
TitleHorizontalAlignment=.5
TitleVerticalAlignment=.49
HorizontalAlignment=.5
VerticalAlignment=.62
WatermarkHorizontalAlignment=.5
WatermarkVerticalAlignment=.35
Transition=none
TransitionDuration=0.0
BackgroundStartColor=0x08090e
BackgroundEndColor=0x08090e
ScaleBackgroundImage=true
ProgressBarBackgroundColor=0x24242c
ProgressBarForegroundColor=0xe84156
ProgressBarWidth=280
ProgressBarHeight=3
ProgressBarHorizontalAlignment=.5
ProgressBarVerticalAlignment=.62
ConsoleLogBackgroundColor=0x08090e
ConsoleLogTextColor=0xeeedf2
DialogClearsFirmwareBackground=true
MessageBelowAnimation=true

[boot-up]
UseEndAnimation=false
UseFirmwareBackground=false

[shutdown]
UseEndAnimation=false
UseFirmwareBackground=false

[reboot]
UseEndAnimation=false
UseFirmwareBackground=false

[updates]
SuppressMessages=true
ProgressBarShowPercentComplete=true
UseProgressBar=true
Title=Installing Updates...
SubTitle=Do not turn off your computer

[system-upgrade]
SuppressMessages=true
ProgressBarShowPercentComplete=true
UseProgressBar=true
Title=Upgrading System...
SubTitle=Do not turn off your computer

[firmware-upgrade]
SuppressMessages=true
ProgressBarShowPercentComplete=true
UseProgressBar=true
Title=Upgrading Firmware...
SubTitle=Do not turn off your computer

[system-reset]
SuppressMessages=true
ProgressBarShowPercentComplete=true
UseProgressBar=true
Title=Resetting System...
SubTitle=Do not turn off your computer
'''


def save(image, path):
    assert not image.isNull(), path
    assert image.save(str(path), 'PNG'), path


def new_image(width, height):
    image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    return image


def render_svg(source, painter, rect):
    renderer = QSvgRenderer(str(source))
    assert renderer.isValid(), source
    renderer.render(painter, rect)


def tint_frame(source, target):
    image = QImage(str(source)).convertToFormat(QImage.Format.Format_ARGB32)
    assert not image.isNull(), source
    for y in range(image.height()):
        for x in range(image.width()):
            pixel = image.pixelColor(x, y)
            light = max(pixel.red(), pixel.green(), pixel.blue()) / 255
            image.setPixelColor(x, y, QColor(round(232 * light), round(65 * light), round(86 * light), pixel.alpha()))
    save(image, target)


def is_blue(pixel):
    return pixel.blue() > pixel.red() * 1.12 and pixel.blue() > pixel.green() * 1.04 and pixel.blue() - pixel.red() > 25


def tint_prompt(source, target):
    image = QImage(str(source)).convertToFormat(QImage.Format.Format_ARGB32)
    assert not image.isNull(), source
    for y in range(image.height()):
        for x in range(image.width()):
            pixel = image.pixelColor(x, y)
            if is_blue(pixel):
                light = max(pixel.red(), pixel.green(), pixel.blue()) / 255
                image.setPixelColor(x, y, QColor(round(232 * light), round(65 * light), round(86 * light), pixel.alpha()))
    save(image, target)


def background(source):
    image = new_image(1920, 1080)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    render_svg(source, painter, QRectF(0, 0, 1920, 1080))
    painter.fillRect(0, 0, 1920, 1080, QColor(5, 6, 10, 195))
    painter.end()
    save(image, DEST / 'background.png')


def watermark(mark):
    image = new_image(560, 238)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    render_svg(mark, painter, QRectF(214, 8, 132, 132))
    font = QFont('Noto Sans', 25, QFont.Weight.Light)
    font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 4.2)
    painter.setFont(font)
    painter.setPen(QColor('#eeedf2'))
    painter.drawText(QRectF(0, 159, 560, 44), Qt.AlignmentFlag.AlignCenter, 'CRIMSON GLASS')
    painter.setPen(QColor('#e84156'))
    painter.drawLine(255, 225, 305, 225)
    painter.end()
    save(image, DEST / 'watermark.png')


def preview(filename, kind='boot'):
    image = QImage(str(DEST / 'background.png'))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    logo = QImage(str(DEST / 'watermark.png'))
    painter.drawImage(round((1920 - logo.width()) / 2), round(1080 * .35 - logo.height() / 2), logo)
    if kind == 'boot':
        spinner = QImage(str(DEST / 'throbber-0009.png'))
        painter.drawImage(944, round(1080 * .62 - 16), spinner)
    elif kind == 'password':
        painter.drawImage(808, round(1080 * .62 - 17), QImage(str(DEST / 'entry.png')))
        painter.drawImage(766, round(1080 * .62 - 17), QImage(str(DEST / 'lock.png')))
        for x in range(849, 919, 14):
            painter.drawImage(x, round(1080 * .62 - 5), QImage(str(DEST / 'bullet.png')))
        painter.setPen(QColor('#eeedf2'))
        painter.setFont(QFont('Noto Sans', 12))
        painter.drawText(QRectF(600, 590, 720, 40), Qt.AlignmentFlag.AlignCenter, 'Unlock the system')
    else:
        painter.setPen(QColor('#eeedf2'))
        painter.setFont(QFont('Noto Sans', 26, QFont.Weight.Light))
        painter.drawText(QRectF(400, 1080 * .49 - 20, 1120, 60), Qt.AlignmentFlag.AlignCenter, 'Installing Updates...')
        painter.setFont(QFont('Noto Sans', 12))
        painter.drawText(QRectF(400, 1080 * .49 + 48, 1120, 40), Qt.AlignmentFlag.AlignCenter, 'Do not turn off your computer')
        painter.fillRect(820, round(1080 * .62), 280, 3, QColor('#24242c'))
        painter.fillRect(820, round(1080 * .62), 176, 3, QColor('#e84156'))
        painter.drawText(QRectF(820, 1080 * .62 + 15, 280, 32), Qt.AlignmentFlag.AlignCenter, '63%')
    painter.end()
    save(image, SCRATCH / filename)


def validate():
    configuration = configparser.ConfigParser()
    configuration.read(DEST / 'crimson-glass.plymouth')
    assert configuration['Plymouth Theme']['ModuleName'] == 'two-step'
    assert configuration['two-step']['ImageDir'] == '/usr/share/plymouth/themes/crimson-glass'
    unchanged = ['bullet.png', 'keymap-render.png']
    for name in unchanged:
        assert (SOURCE / name).read_bytes() == (DEST / name).read_bytes(), name
    count = 0
    for source in sorted(SOURCE.glob('*.png')):
        image = QImage(str(DEST / source.name))
        assert not image.isNull(), source.name
        if source.name.startswith(('animation-', 'throbber-')):
            before = QImage(str(source))
            assert image.size() == before.size(), source.name
            for y in range(before.height()):
                for x in range(before.width()):
                    assert image.pixelColor(x, y).alpha() == before.pixelColor(x, y).alpha(), source.name
            count += 1
        elif source.name in ('entry.png', 'lock.png', 'capslock.png', 'keyboard.png'):
            before = QImage(str(source))
            assert image.size() == before.size(), source.name
            for y in range(before.height()):
                for x in range(before.width()):
                    original = before.pixelColor(x, y)
                    actual = image.pixelColor(x, y)
                    assert actual.alpha() == original.alpha(), source.name
                    if not is_blue(original):
                        assert actual == original, source.name
    for mode in ('updates', 'system-upgrade', 'firmware-upgrade', 'system-reset'):
        assert configuration[mode].getboolean('UseProgressBar')
        assert configuration[mode]['SubTitle'] == 'Do not turn off your computer'
    result = {'native_plugin': 'two-step', 'recolored_frames': count, 'unchanged_input_assets': unchanged,
              'prompt_geometry_alpha_and_nonblue_pixels_preserved': True,
              'all_pngs_decode': True, 'frame_alpha_preserved': True, 'update_modes': 4,
              'image_dir': configuration['two-step']['ImageDir'],
              'preview_type': 'Qt composition of the actual PNG assets, not a running Plymouth daemon',
              'sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(DEST.iterdir()) if p.is_file()}}
    (SCRATCH / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'sha256'}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mark', type=Path, default=SHARED_MARK)
    parser.add_argument('--background', type=Path, default=ROOT / 'sources/art/crimson-wallpaper.svg')
    args = parser.parse_args()
    assert args.mark.is_file(), f'Missing shared monogram: {args.mark}'
    DEST.mkdir(parents=True, exist_ok=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    for source in SOURCE.glob('*.png'):
        if source.name.startswith(('animation-', 'throbber-')):
            tint_frame(source, DEST / source.name)
        elif source.name in ('entry.png', 'lock.png', 'capslock.png', 'keyboard.png'):
            tint_prompt(source, DEST / source.name)
        elif source.name != 'watermark.png':
            shutil.copy2(source, DEST / source.name)
    background(args.background)
    watermark(args.mark)
    (DEST / 'crimson-glass.plymouth').write_text(THEME)
    (DEST / 'ASSET-ORIGINS.txt').write_text(
        'Crimson Glass Plymouth theme\n\n'
        'Native animation and input PNG assets adapted from the installed Plymouth spinner theme\n'
        '(Plymouth 26.134.222; GPL-2.0-or-later; https://gitlab.freedesktop.org/plymouth/plymouth).\n'
        'Input, keyboard, lock and caps-lock PNGs retain source geometry and transparency;\n'
        'only blue accent pixels become crimson. Bullet and keymap-render PNGs are unmodified.\n'
        'Spinner and end-animation frames have a crimson tint with source transparency preserved.\n'
        'Crimson Glass monogram, wordmark and ribbon background are locally created theme art.\n'
        'Artwork is rendered using Qt SVG/QPainter. No daemon, bootloader, or system config is modified by the build.\n')
    preview('boot-layout.png')
    preview('password-layout.png', 'password')
    preview('updates-layout.png', 'updates')
    validate()


if __name__ == '__main__':
    app = QGuiApplication([])
    main()
