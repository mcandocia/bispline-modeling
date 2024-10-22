import math
import re

from tools import clns
from tools import clear_empty
from tools import extract_degree

# this file contains additional structure-creating code
# that feeds into segments.py but would otherwise
# make it harder to read

kd_base_template = """
    // this defines how many iterations the kernel goes through
    // and assigns the initial parameters
    // note that while a denominator is still calculated for edge segments,
    // they will not be evaluated for them
    {title}
    {kernel_dimensions}
"""

kdT0_d0_template = """
    {title}
    // template for squares
    for (yi in 1:{nky}){{
      for (xi in 1:{nkx}){{
        // for each specific subkernel
        // loop over max distance in each direction

        for (y in max(1, 1+(yi - 1) * {kD} - {max_range}):min(ydim,1+(yi - 1) * {kD} + {max_range})){{
          for (x in max(1, 1+(xi - 1) * {kD} - {max_range}):min(xdim,1+(xi - 1) * {kD} + {max_range})){{
            // note the center is (1+(yi-1)*{kD},(1+(xi-1)*{kD})
            {kmxv}[y,x] += (1.0-{kR} * max(abs(y-(1+yi-1)*{kD}),abs(x-(1+(xi-1)*{kD}))));
          }}
        }}
      }}
    }}
"""

kdT0_d1_template = """
    {title}
    // template for squares
    // first derivative, so just do a flat count 
    for (yi in 1:{nky}){{
      for (xi in 1:{nkx}){{
        // for each specific subkernel
        // loop over max distance in each direction

        for (y in max(1, 1+(yi - 1) * {kD} - {max_range}):min(ydim,1+(yi - 1) * {kD} + {max_range})){{
          for (x in max(1, 1+(xi - 1) * {kD} - {max_range}):min(xdim,1+(xi - 1) * {kD} + {max_range})){{
            // note the center is (1+(yi-1)*{kD},(1+(xi-1)*{kD})
            {kmxv}[y,x] += 1;
          }}
        }}
      }}
    }}
"""

kdT1_template = """
// TODO: develop later

"""

kdT2_template = """
// TODO: develop later

"""

def build_kernel_denominator_loop(opt,degree_prefix,varname,ki):

    kD, kR, kT, dflag, max_range, normal_sd = opt
    degree_x = extract_degree(degree_prefix,'x')
    degree_y = extract_degree(degree_prefix,'y')
    d = degree_x + degree_y

    # this makes it easier to read the code
    title=f'//kernel #{ki+1} degrees {degree_prefix} (sum={d})|dflag={dflag}'

    # values to assign (number of kernels in each direction)
    ksx = f'xdim %/% {kD}+1;'
    ksy = f'ydim %/% {kD}+1;'

    # IMPORTANT VARIABLES TO REUSE ELSEWHERE
    kxv = f'kx_{ki}'
    kyv = f'ky_{ki}'

    # definition and assignemtn
    ksxi = f'int<lower=1> {kxv};'
    ksyi = f'int<lower=1> {kyv};'

    ksxia = f'{kxv} = {ksx};'
    ksyia = f'{kyv} = {ksy};'

    # denominators
    kmxv = f'kernel_d{degree_prefix}_{ki}'
    kmxvi = f'matrix<lower=0>[ydim,xdim] {kmxv};'

    # assign 0s to denominator matrix initially
    kmxvia = f"""
    for (yi in 1:ydim){{
      for (xi in 1:xdim){{
        {kmxv}[yi,xi] = 0;
      }}
    }}
    """

    # TODO: omit kernel denominators if flag is disabled
    # assigns kernel sizes
    # skips re-defining kernels of different orders
    base_definitions = kd_base_template.format(
        title=title,
        kernel_dimensions = '\n'.join(clear_empty([
            ksyi * (d==0),
            ksxi * (d==0),
            ksyia * (d==0),
            ksxia * (d==0),
            kmxvi,
            kmxvia,            
        ]))
    )

    # square (T=0)
    if kT == 0:
        # evaluate max range (x OR y)
        #max_range = math.floor(kD / kR)
        if d == 0:
            kernel_template = kdT0_d0_template.format(
                title=title,
                kD=kD,
                kR=kR,
                kmxv=kmxv,
                max_range=max_range,
                nky = kyv,
                nkx = kxv,
            )
        elif d == 1:
            kernel_template = kdT0_d1_template.format(
                title=title,
                kD=kD,
                kR=kR,
                kmxv=kmxv,
                max_range=max_range,
                nky = kyv,
                nkx = kxv,                
            )
        else:
            return ''

    # diamond (T=1)
    if kT == 1:
        # evaluate max range (x + y)
        raise NotImplementedError('Kernel of Type 1 (diamond) not yet implemented!')

    # circle (T=2)
    if kT == 2:
        # evaluate max range (sqrt(x^2 + y^2))
        raise NotImplementedError('Kernel of Type 2 (circle) not yet implemented!')

    full_kernel_initialization = '\n'.join([
        base_definitions,
        kernel_template,
    ])

    return full_kernel_initialization

def initialize_kernel(opt, ki):
    kD, kR, kT, dflag, max_range, normal_sd = opt    
    vname = f'kernel_{ki}'
    kxv = f'kx_{ki}'
    kyv = f'ky_{ki}'
    return clns("""
    matrix[{kyv},{kxv}] {vname};
    """)

klT0_template = """
{title}
// template for squares
for (yi in 1:{nky}){{
  for (xi in 1:{nkx}){{
    // for each subkernel loop
        for (y in max({tb}, 1+(yi - 1) * {kD} - {max_range}):min({lb},1+(yi - 1) * {kD} + {max_range})){{
          for (x in max({lb}, 1+(xi - 1) * {kD} - {max_range}):min({rb},1+(xi - 1) * {kD} + {max_range})){{
            // note the center is (1+(yi-1)*{kD},(1+(xi-1)*{kD})
            {mapname}[y,x] += {kname}[yi,xi] * {value_function};
          }}
        }}
  }}
}}

"""

klT1_template = """
// TODO: develop later
"""

klT2_template = """
// TODO: develop later
"""

def build_kernel_loop(opt,degree_prefix,varname,ki):
    kD, kR, kT, dflag, max_range, normal_sd = opt
    degree_x = extract_degree(degree_prefix,'x')
    degree_y = extract_degree(degree_prefix,'y')
    d = degree_x + degree_y

    top = 'T' in options['existing_edges']
    bot = 'B' in options['existing_edges']
    left = 'L' in options['existing_edges']
    right = 'R' in options['existing_edges']
    n_vertical = top + bot
    n_horizontal = left + right
    kname = f'kernel_{ki}'

    if top:
        tb = '2'
    else:
        tb = '1'
    if bot:
        bb = 'ydim'
    else:
        bb = 'ydim-1'
    if left:
        lb = '2'
    else:
        lb = '1'
    if right:
        rb = 'xdim-1'
    else:
        rb='xdim'

    # this makes it easier to read the code
    title=f"""//kernel #{ki+1} degrees {degree_prefix} (sum={d})|dflag={dflag}
//tblr={tb}{bb}{lb}{rb}"""

    # values to assign (number of kernels in each direction)
    #ksx = f'xdim %/% {kD}+1;'
    #ksy = f'ydim %/% {kD}+1;'

    # IMPORTANT VARIABLES TO REUSE ELSEWHERE
    kxv = f'kx_{ki}'
    kyv = f'ky_{ki}'

    # definition and assignemtn
    #ksxi = f'int<lower=1> {kxv};'
    #ksyi = f'int<lower=1> {kyv};'

    #ksxia = f'{kxv} = {ksx};'
    #ksyia = f'{kyv} = {ksy};'

    # denominators
    kmxv = f'kernel_d{degree_prefix}_{ki}'
    #kmxvi = f'matrix<lower=0>[ydim,xdim] {kmxv};'

    if kT == 0:
        mapname = f'map_{degree_prefix}'        
        if d == 0:
            #value function
            value_function = f'(1.0-{kR} * max(abs(y-(1+yi-1)*{kD}),abs(x-(1+(xi-1)*{kD}))))'
            kernel_lines = klT0_template.format(
                title=title,
                nky=kyv,
                nkx=kxv,
                max_range = max_range,
                mapname=mapname,
                value_function=value_function,
                kname=kname,
            )
        elif d == 1:
            # x derivative
            if degree_x == 1:
                # if x < center, + * kernel strength
                # if x > center, - * kernel strength
                value_function = f'sign(1+(xi-1) * {kD} - x)'

            # y derivative
            if degree_y == 1:
                # if y < center, + * kernel strength
                # if y > center, - * kernel strength
                value_function = f'sign(1+(yi-1) * {kD} - y)'
            
            kernel_lines = klT0_template.format(
                title=title,
                nky=kyv,
                nkx=kxv,
                max_range = max_range,
                mapname=mapname,
                value_function=value_function,
                kname=kname,
            )            
        else:
            kernel_lines = ''
        
    # diamond (T=1)
    if kT == 1:
        # evaluate max range (x + y)
        raise NotImplementedError('Kernel of Type 1 (diamond) not yet implemented!')

    # circle (T=2)
    if kT == 2:
        # evaluate max range (sqrt(x^2 + y^2))
        raise NotImplementedError('Kernel of Type 2 (circle) not yet implemented!')

    return kernel_lines

