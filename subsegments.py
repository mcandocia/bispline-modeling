import math
import re

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

    # assigns kernel sizes
    # skips re-defining kernels of different orders
    base_definitions = kd_base_template.format(
        title=title,
        kernel_dimensions = '\n'.join([
            ksyi * (d==0),
            ksxi * (d==0),
            ksyia * (d==0),
            ksxia * (d==0),
            kmxvi,
            kmxvia,            
        ])
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

def build_kernel_loop(opt,degree_prefix,varname,ki):
    pass
