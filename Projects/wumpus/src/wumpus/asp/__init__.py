from .lite import unlite

__all__ = ['unlite']

def unlit(fname):
    with open(fname, 'r') as f:
        return [ln[4:-1] if ln.startswith('    ') else '%' + ln[:-1] for ln in f]
