def rgb2hex(c): return '#'+''.join([hex(b).strip('0x').zfill(2) for b in c])

def lerp(x,a,b,c,d):
    if b - a == 0:
        return 0
    return (x-a)*(d-c)/(b-a)+c

def cap(x,a,b):
    if x > b: return b
    elif x < a: return a
    else: return x
