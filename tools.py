import itertools
from collections import Counter
import re

TOOLS_DEBUG=False

def clear_empty(x):
    return [
        e for e in x
        if e
    ]

def clear_leading_newline_spaces(x):
    return re.sub(
        r'^[ \t +]',
        '',
        x,
        flags=re.M
    )

# alias
clns = clear_leading_newline_spaces

def print_fl(x,margin=10,**kwargs):
    if len(x) <= 2*margin:
        print(x,**kwargs)
    else:
        if isinstance(x, str):
            print(x[:margin] + '...' + x[-margin:])
        else:
            print(x[:margin] + ['...'] + x[-margin:])


def degree_derivative_iter_max(k, v=['y','x'],sep='',sep2=''):
    # choose all combinations where max <= k
    # e.g., x0y0
    # x1y0
    # x1y1z1
    n = len(v)
    vrange = list(range(k+1))
    combos = list(itertools.combinations_with_replacement(vrange,n))
    res = [
        sep.join(
            ['%s%s%s' % (v[i], sep2,c[i])  for i in range(len(c))]
        ) for c in combos
    ]
    return res

def degree_derivative_iter_sum(k, v=['y','x'],sep='',sep2=''):
    # choose all combinations where sum == k
    # e.g., x0y0
    # x1y0
    # x1y1z1
    n = len(v)
    vrange = list(range(k+1))
    res = []
    if len(v) == 1:
        return ['%s%s%s' % (v[0],sep2,k)]
    if len(v) == 2:
        # iterate through each combination
        res.extend([
            '%s%s%s' % (v[0],sep2,i) + sep + '%s%s%s' % (v[1],sep2,k-i)
            for i in range(k+1)
        ])
    else:
        for sub_k in range(k+1):
            if TOOLS_DEBUG:
                #print('subk')
                #print(sub_k)
                pass
            candidates = [
                '%s%s%s' % (v[0],sep2,i) + sep + '%s%s%s' % (v[1],sep2,sub_k-i)
                for i in range(sub_k+1)
            ]
            if TOOLS_DEBUG:
                #print('Candidates:')
                #print(candidates)
                pass
            sub_branches = [
                candidate + e
                for candidate in candidates
                for e in 
                degree_derivative_iter_sum(
                    k-sub_k,
                    v[2:],
                    sep=sep,
                    sep2=sep2
                )
            ]
            res.extend(sub_branches)
    return res

def extract_degree(x, v):
    return int(re.findall('%s([0-9]+)' % v, x)[0])

# conversion of dictionaries to tuples used for kernel options
def dict_to_kopts(x):
    return {}
            
        
        

if __name__ == '__main__':
    TOOLS_DEBUG=True
    print('testing...')
    print(extract_degree('y3x4','x'))
    print(degree_derivative_iter_max(4))
    print(degree_derivative_iter_max(4,'xyz'))

    print(degree_derivative_iter_sum(3,'xy'))
    print(degree_derivative_iter_sum(3,'xyz'))
    print(degree_derivative_iter_sum(5,'xyz'))
    print_fl(degree_derivative_iter_sum(7,'tuvxyz'))
    
