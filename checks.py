import argparse
import re

def check_odd(x):
    msg = 'Argument must be a postive, odd integer, not %s!'
    try:
        x = int(x)
    except:
        raise argparse.ArgumentTypeError(msg % x)
    if type(x) != type(1):
        raise argparse.ArgumentTypeError(msg % x)
    if x < 1 or x % 2 != 1:
        raise argparse.ArgumentTypeError(msg % x)
    return int(x)

def check_whole(x):
    msg = 'Argument must be a non-negative integer, not %s!'
    if type(x) != type(1):
        raise argparse.ArgumentTypeError(msg % x)
    if x < 0:
        raise argparse.ArgumentTypeError(msg % x)
    return int(x)

def check_sd(x):
    msg = 'Argument must be a non-negative number, not %s!' 
    try:
        assert float(x) >= 0
    except:
        raise argparse.ArgumentTypeError(msg % x)
    return float(x)
            

def check_real_under_1(x):
    msg = 'Argument must be non-negative number less than 1, not %s'
    try:
        x = float(x)
        assert x >= 0 and x < 1
    except:
        raise argparse.ArgumentTypeError(msg % str(x))
    return float(x)


def check_kernel(x):
    # 3-tuple (spacing,decay rate,type)
    mstring = r'\(([0-9]+),([0-9]+(?:\.[0-9]+)?),([012])\)'
    # 6-tuple  ([3-tuple],
    #           denominator flag,
    #           max_range [default spacing // rate],
    #           normal_sd [for type=2 only, default spacing/2))
    mstring_alt = r'\(([0-9]+),([0-9]+(?:\.[0-9]+)?),([012]),([01]),([0-9]+),([0-9]+(?:\.[0-9]+)?)\)'
    msg = 'Argument must be in format of (integer,real,one of {0,1,2}), not %s; or 6-tuple with those initial elements followed by (one of {0,1} (denominator flag), pos. integer (max range), pos. real (type 2 SD decay))'
    elem = x
    if not re.match(mstring,elem):
        if re.match(mstring_alt, elem):
            parsed = [
                (int(e[0]),float(e[1]),int(e[2]), int(e[3]),int(e[4]),float(e[5]))
                for e in 
                re.findall(mstring_alt,elem)
            ][0]            
            
        else:
            raise argparse.ArgumentTypeError(msg % str(elem))
    else:
        parsed = [
            (int(e[0]),float(e[1]),int(e[2]))
            for e in 
            re.findall(mstring,elem)        
        ][0]
        parsed = list(parsed) + [1,parsed[1]//2,parsed[1]/2]

    return list(parsed)


if __name__=='__main__':
    print('basic kernel tests')
    print(check_kernel('(2,3,0)'))
    print(check_kernel('(2,3,0,1,2,3)'))
