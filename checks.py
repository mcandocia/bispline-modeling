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
    mstring = r'\(([0-9]+),([0-9]+(?:\.[0-9]+)?),([012])\)'
    msg = 'Argument must be in format of (integer,real,one of {0,1,2}), not %s'
    elem = x
    if not re.match(mstring,elem):
        raise argparse.ArgumentTypeError(msg % str(elem))
    parsed = [
        (int(e[0]),float(e[1]),int(e[2]))
        for e in 
        re.findall(mstring,elem)        
    ][0]

    return parsed
