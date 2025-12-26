# ico_dump.py
import struct, sys

def list_sizes(ico):
    with open(ico, 'rb') as f:
        hdr = f.read(6)
        _, count = struct.unpack('<HH', hdr)
        print(f'共 {count} 张图标：')
        for i in range(count):
            width, height, colors, reserved, planes, bpp, size, offset = \
                struct.unpack('<BBBBHHII', f.read(16))
            w = width or 256          # 0 代表 256
            h = height or 256
            print(f'  {i+1}: {w}×{h}  {bpp}bpp  大小 {size} bytes')

if __name__ == '__main__':
    list_sizes(sys.argv[1] if len(sys.argv) > 1 else 'AutoTool_AB_Icon_128.ico')