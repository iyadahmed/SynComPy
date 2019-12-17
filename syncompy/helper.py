def rgb2hex(c): return '#'+''.join([hex(b).strip('0x').zfill(2) for b in c])

def lmap(x,a,b,c,d): return (x-a)*(d-c)/(b-a)+c

def cap(x,a,b):
    if x > b: return b
    elif x < a: return a
    else: return x

class bswitch(object):
    def __init__(self, value):
        self._last = value
    def update(self, value):
        if self._last != value:
            if value:
                self._out = 1
            else:
                self._out = -1
        else:
            self._out = 0
        self._last = value
        return self._out
