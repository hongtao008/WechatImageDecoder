#!/usr/bin/env python
# zhangxiaoyang.hit[at]gmail.com

#微信图片解码
#https://github.com/zhangxiaoyang/WechatImageDecoder

import re
import os

class WechatImageDecoder:
    def __init__(self, dat_file, outPath):
        dat_file = dat_file.lower()       
        
        #创建输出目录       
        if  not os.path.exists(outPath):
            os.makedirs(outPath)
        
        decoder = self._match_decoder(dat_file)
        decoder(dat_file)

    def _match_decoder(self, dat_file):
        decoders = {
            r'.+\.dat$': self._decode_pc_dat,
            r'cache\.data\.\d+$': self._decode_android_dat,
            None: self._decode_unknown_dat,
        }

        for k, v in decoders.items():
            if k is not None and re.match(k, dat_file):
                return v
        return decoders[None]

    def _decode_pc_dat(self, dat_file):
        
        def do_magic(header_code, buf):
            return header_code ^ list(buf)[0] if buf else 0x00
        
        def decode(magic, buf):
            return bytearray([b ^ magic for b in list(buf)])
            
        def guess_encoding(buf):
            headers = {
                'jpg': (0xff, 0xd8),
                'png': (0x89, 0x50),
                'gif': (0x47, 0x49),
            }
            for encoding in headers:
                header_code, check_code = headers[encoding] 
                magic = do_magic(header_code, buf)
                _, code = decode(magic, buf[:2])
                if check_code == code:
                    return (encoding, magic)
            print('Decode failed')
            sys.exit(1) 

        with open(dat_file, 'rb') as f:
            buf = bytearray(f.read())
        file_type, magic = guess_encoding(buf)

        img_file = re.sub(r'.dat$', '.' + file_type, dat_file)
        img_file = outPath + "/" + os.path.basename(img_file)
        with open(img_file, 'wb') as f:
            new_buf = decode(magic, buf)
            f.write(new_buf)

    def _decode_android_dat(self, dat_file):
        with open(dat_file, 'rb') as f:
            buf = f.read()

        last_index = 0
        for i, m in enumerate(re.finditer(b'\xff\xd8\xff\xe0\x00\x10\x4a\x46', buf)):
            if m.start() == 0:
                continue

            imgfile = '%s_%d.jpg' % (dat_file, i)
            with open(imgfile, 'wb') as f:
                f.write(buf[last_index: m.start()])
            last_index = m.start()

    def _decode_unknown_dat(self, dat_file):
        raise Exception('Unknown file type')


if __name__ == '__main__':
    import sys
    import os
    
    if len(sys.argv) != 3 and len(sys.argv) !=2:
        print('\n'.join([
            'Usage:',
            '  python WechatImageDecoder.py [imgPath] [outPath]',
            '',
            'Example:',
            '  # PC:',
            '  python WechatImageDecoder.py R:\DataPath r:\DecodedPath',
            '',
            '  # Android:',
            '  python WechatImageDecoder.py cache.data.10'
        ]))
        sys.exit(1)
    
    if len(sys.argv) == 3:
        _,  path, outPath = sys.argv[:3]
    else:
        _, path = sys.argv[:2]
        outPath = path
    
    files= os.listdir(path) #得到文件夹下的所有文件名称
   
    s = []
    for file in files: #遍历文件夹
         if not os.path.isdir(file): #判断是否是文件夹，不是文件夹才打开
              #s.append(file) #每个文件的文本存到list中
              try:
                    WechatImageDecoder(path + "/" + file,  outPath)
                    print(file)
              except Exception as e:
                    print(e)                    
                    s.append(file)
                    #sys.exit(1)
    if len(s) > 0:
        print("转换失败的文件:")
        print(s) #打印结果
    
    sys.exit(0)

