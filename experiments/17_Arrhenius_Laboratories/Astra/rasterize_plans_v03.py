"""Render our mesh-derived SVG subset with installed Windows GDI+, no browser."""
import ctypes as C
from pathlib import Path
import xml.etree.ElementTree as ET

gd = C.WinDLL('gdiplus')
P, I, U, F = C.c_void_p, C.c_int, C.c_uint, C.c_float
class Point(C.Structure):
    _fields_ = [('x', F), ('y', F)]
class Rect(C.Structure):
    _fields_ = [('x', F), ('y', F), ('width', F), ('height', F)]
class Startup(C.Structure):
    _fields_ = [('version', U), ('callback', P), ('no_thread', I), ('no_codecs', I)]
class Guid(C.Structure):
    _fields_ = [('a', U), ('b', C.c_ushort), ('c', C.c_ushort), ('d', C.c_ubyte * 8)]
def api(name, types, *args):
    fn = getattr(gd, name)
    fn.argtypes = types
    fn.restype = I
    status = fn(*args)
    if status: raise RuntimeError(f'{name}: GDI+ status {status}')
def color(value, opacity=1):
    value = value.lstrip('#')
    if len(value) == 3: value = ''.join(c*2 for c in value)
    return (round(255*float(opacity)) << 24) | int(value, 16)
def brush(value):
    handle = P()
    api('GdipCreateSolidFill', [U, C.POINTER(P)], value, C.byref(handle))
    return handle
def draw(node, graphics, clip):
    tag, a = node.tag.split('}')[-1], node.attrib
    if tag in ('defs', 'clipPath'): return
    if tag == 'g':
        if 'clip-path' in a:
            api('GdipSetClipRect', [P,F,F,F,F,I], graphics, *clip, 0)
        for child in node: draw(child, graphics, clip)
        api('GdipResetClip', [P], graphics)
        return
    if tag == 'rect':
        b = brush(color(a['fill']))
        xywh = [float(a.get('x',0)),float(a.get('y',0)),1300 if a['width']=='100%' else float(a['width']),1000 if a['height']=='100%' else float(a['height'])]
        api('GdipFillRectangle', [P,P,F,F,F,F], graphics,b,*xywh)
        api('GdipDeleteBrush',[P],b)
    elif tag in ('polygon','polyline'):
        points = [Point(*map(float, pair.split(','))) for pair in a['points'].split()]
        array = (Point * len(points))(*points)
        if a.get('fill','none') != 'none':
            b = brush(color(a['fill']))
            api('GdipFillPolygon',[P,P,C.POINTER(Point),I,I],graphics,b,array,len(points),0)
            api('GdipDeleteBrush',[P],b)
        if a.get('stroke','none') != 'none':
            pen = P()
            api('GdipCreatePen1',[U,F,I,C.POINTER(P)],color(a['stroke'],a.get('stroke-opacity',1)),float(a['stroke-width']),2,C.byref(pen))
            if a.get('stroke-linecap') == 'round': api('GdipSetPenLineCap197819',[P,I,I,I],pen,2,2,0)
            if a.get('stroke-linejoin') == 'round': api('GdipSetPenLineJoin',[P,I],pen,2)
            fn = 'GdipDrawPolygon' if tag == 'polygon' else 'GdipDrawLines'
            api(fn,[P,P,C.POINTER(Point),I],graphics,pen,array,len(points))
            api('GdipDeletePen',[P],pen)
    elif tag == 'text':
        family,font,fmt = P(),P(),P()
        size = float(a['font-size'])
        api('GdipCreateFontFamilyFromName',[C.c_wchar_p,P,C.POINTER(P)],a.get('font-family','Arial'),None,C.byref(family))
        api('GdipCreateFont',[P,F,I,I,C.POINTER(P)],family,size,0,2,C.byref(font))
        api('GdipStringFormatGetGenericTypographic',[C.POINTER(P)],C.byref(fmt))
        middle = a.get('text-anchor') == 'middle'
        api('GdipSetStringFormatAlign',[P,I],fmt,1 if middle else 0)
        b = brush(color(a.get('fill','#000000')))
        x = float(a['x']) - (400 if middle else 0)
        rect = Rect(x,float(a['y'])-size*.93,800 if middle else 1250-x,size*2)
        api('GdipDrawString',[P,C.c_wchar_p,I,P,C.POINTER(Rect),P,P],graphics,node.text,-1,font,C.byref(rect),fmt,b)
        for name,handle in [('GdipDeleteBrush',b),('GdipDeleteStringFormat',fmt),('GdipDeleteFont',font),('GdipDeleteFontFamily',family)]: api(name,[P],handle)
    else:
        for child in node: draw(child,graphics,clip)

token = C.c_size_t()
api('GdiplusStartup',[C.POINTER(C.c_size_t),C.POINTER(Startup),P],C.byref(token),C.byref(Startup(1,None,0,0)),None)
png = Guid(0x557cf406,0x1a04,0x11d3,(C.c_ubyte*8)(0x9a,0x73,0,0,0xf8,0x1e,0xf3,0x2e))
for source in sorted(Path(__file__).parent.glob('plan_v03_*.svg')):
    root = ET.parse(source).getroot()
    clipnode = next(e for e in root.iter() if e.tag.endswith('clipPath'))[0]
    clip = [float(clipnode.attrib[k]) for k in ('x','y','width','height')]
    bitmap,graphics = P(),P()
    api('GdipCreateBitmapFromScan0',[I,I,I,I,P,C.POINTER(P)],1300,1000,0,0x26200a,None,C.byref(bitmap))
    api('GdipGetImageGraphicsContext',[P,C.POINTER(P)],bitmap,C.byref(graphics))
    api('GdipSetSmoothingMode',[P,I],graphics,4)
    api('GdipSetTextRenderingHint',[P,I],graphics,4)
    draw(root,graphics,clip)
    output = source.with_suffix('.png')
    api('GdipSaveImageToFile',[P,C.c_wchar_p,C.POINTER(Guid),P],bitmap,str(output),C.byref(png),None)
    api('GdipDeleteGraphics',[P],graphics)
    api('GdipDisposeImage',[P],bitmap)
    print(output.name, flush=True)
gd.GdiplusShutdown(token)
