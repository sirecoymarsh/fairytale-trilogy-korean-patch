"""Sample only the movie surface of the verified installed collection window."""
from pathlib import Path
import ctypes
import sys
import time
import win32gui
import win32process
import win32ui
import win32con
from PIL import Image, ImageChops, ImageGrab, ImageStat

pid, window = map(int, sys.argv[1:3])
assert win32process.GetWindowThreadProcessId(window)[1] == pid
assert win32gui.GetWindowText(window) == '페어리테일 통합판'
user = ctypes.windll.user32
user.SetProcessDPIAware()
width, height = win32gui.GetClientRect(window)[2:]
client_x, client_y = win32gui.ClientToScreen(window, (0, 0))
outer = win32gui.GetWindowRect(window)
folder = Path(__file__).resolve().parent / 'qa' / 'integrated'

def captured(method):
    if method == 'foreground':
        if win32gui.GetForegroundWindow() != window:
            return None
        return ImageGrab.grab((client_x, client_y, client_x + width, client_y + height), all_screens=True).convert('RGB')
    bounds = (outer[2]-outer[0],outer[3]-outer[1]) if method==2 else (width,height)
    dc = win32gui.GetDC(window)
    src = win32ui.CreateDCFromHandle(dc)
    dst = src.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(src, *bounds)
    dst.SelectObject(bitmap)
    try:
        if method == 'windowdc':
            dst.BitBlt((0, 0), (width, height), src, (0, 0), win32con.SRCCOPY)
        else:
            user.PrintWindow(window, dst.GetSafeHdc(), method)
        im = Image.frombytes('RGB', bounds, bitmap.GetBitmapBits(True), 'raw', 'BGRX', 0, 1)
        if method==2:
            x,y=client_x-outer[0],client_y-outer[1]
            im=im.crop((x,y,x+width,y+height))
        return im
    finally:
        dst.DeleteDC()
        src.DeleteDC()
        win32gui.ReleaseDC(window, dc)
        win32gui.DeleteObject(bitmap.GetHandle())

def group():
    samples = {}
    for method in (3, 2, 'windowdc', 'foreground'):
        im = captured(method)
        if im is not None:
            samples[method] = im.crop((width//10, height//10, 9*width//10, 8*height//10))
    return samples

first = group()
time.sleep(3.1)
last = group()
for method in first.keys() & last.keys():
    delta = max(ImageStat.Stat(ImageChops.difference(first[method], last[method])).mean)
    print('capture',method,'visible frame difference',round(delta,2),flush=True)
    if delta > 1.2 and max(ImageStat.Stat(last[method]).stddev) > 10:
        first[method].save(folder / 'installed-encore-opening-1.png')
        last[method].save(folder / 'installed-encore-opening-2.png')
        sys.exit(0)
raise RuntimeError('Window capture did not provide distinct video frames')
