from os             import chmod, getcwd
from os.path        import isfile, join
from shutil         import which
from stat           import S_IRGRP, S_IRWXU, S_IWGRP
from sys            import platform, maxsize
from urllib.request import urlopen

def downloadDlv(fname):
    # Taken from http://www.dlvsystem.com/dlv/
    if platform.startswith('linux'):
        if maxsize == 2 ** 31 - 1:
            url = 'http://www.dlvsystem.com/files/dlv.i386-linux-elf-static.bin'
        else:
            url = 'http://www.dlvsystem.com/files/dlv.x86-64-linux-elf-static.bin'
    if platform.startswith('darwin'):
        url = 'http://www.dlvsystem.com/files/dlv.i386-apple-darwin.bin'
    if platform.startswith('cygwin') or platform.startswith('win'):
        url = 'http://www.dlvsystem.com/files/dlv.mingw.exe'

    res = urlopen(url)

    if res.status != 200:
        print('Failed to download DLV! GET {} resulted in HTTP {}'.format(url, res.status))
        return

    with open(fname, 'wb') as f:
        f.write(res.read())

def dlv():
    here = join(getcwd(), 'dlv')
    fname = which('dlv')

    if fname != None:
        return fname
    if isfile(here):
        return here
    else:
        print('NOTE: Could not find DLV! Will attempt to download it.')
        downloadDlv(here)
        chmod(here, S_IRGRP | S_IRWXU | S_IWGRP)
        return here
