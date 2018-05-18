from os      import chmod, getcwd
from os.path import isfile, join
from shutil  import which
from stat    import S_IRGRP, S_IRWXU, S_IWGRP
from sys     import platform, maxsize

from requests import get

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

    res = get(url, stream=True)
    res.raise_for_status()

    with open(fname, 'wb') as f:
        for b in res.iter_content(1024):
            f.write(b)

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
