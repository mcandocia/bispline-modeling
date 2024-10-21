import re
from tools import degree_derivative_iter_max
from tools import degree_derivative_iter_sum

from subsegments import build_kernel_denominator_loop
from subsegments import build_kernel_loop


DATA_SEGMENT_TEMPLATE = """

   // edges will overlay the parameter grid, but keep data, even perfect grids,
   // intact
   int<lower=1> ydim;
   int<lower=1> xdim;

   // if use_perfect_grid
   {mask}
   {known_map}
   // if NOT use_perfect_grid
   {N}
   {ycoords}
   {xcoords}

   // if using time drift
   {time}
   // if phi will be defined
   // TODO: add parameter counterpart in parameters section
   {phi_if_defined}

   // derivative penalties (if defined)
   // TODO: add parameter counterparts
   {defined_derivatives}

   // various edge inputs
   {edge_definitions}

   // drift
   {drift_sd}
   {drift_tile_radius}

   // granularity
   int<lower=1> granularity;

"""

# TODO: test
def build_data_segment(options):
    extra_edges = bool(options['existing_edges'])
    # I'll avoid using these for ease of programming
    if extra_edges:
        ee = '0'
    else:
        ee = ''

    if options['phi'] or options['estimate_phi']:
        use_phi = True
    else:
        use_phi = False

    # building actual parts of template
    
    if options['use_perfect_grid']:
        # note: if edges are defined, then
        # expanded version of mask will be defined later
        mask = f'mask = matrix[ydim][xdim]'
        known_map = f'known_map = matrix[ydim][xdim]'
        xcoords = ''
        ycoords = ''
        phi_if_defined = ''
        N = ''
    else:
        mask = ''
        known_map = ''
        # note: to avoid problems with points going out of bounds,
        # those values will use extrapolations which may be prone to error
        #
        N = 'int N;'
        xcoords = 'vector[N]<lower=0> xcoords;'
        ycoords = 'vector[N]<lower=0> ycoords;'
        if use_phi:
            time = 'vector[N]<lower=0> td;'
            if use_phi and not options['estimate_phi']:
                phi_if_defined = 'real phi;'
            else:
                phi_if_defined = ''
        else:
            phi_if_defined = ''

        if options['drift_sd']:
            drift_sd = 'real<lower=0> drift_sd;'
            if options['sample_data_tile_radius']:
                drift_tile_radius = 'int drift_tile_radius;'
            else:
                drift_tile_radius = ''
        else:
            drift_sd = ''
            drift_tile_radius = ''
    if (options['drift_sd'] > 0) or use_phi:
        time = 'vector[N] td;'
    else:
        time = ''
        

    if options['derivative_penalties']:
        defined_derivatives = '\n'.join(
            ['W_d%s' % d for d in options['derivative_penalties']]
        )
    else:
        defined_derivatives = ''

    if options['existing_edges']:
        top = 'T' in options['existing_edges']
        bot = 'B' in options['existing_edges']
        left = 'L' in options['existing_edges']
        right = 'R' in options['existing_edges']

        n_vertical = top + bot
        n_horizontal = left + right
        edge_list = []

        # add edges for each combination of derivative
        # (e.g., edge_T_x0y0, edge_B_x1y2
        if top:
            edge_list.append(f'row_vector[xdim]edge_top;')
        if bot:
            edge_list.append(f'row_vector[xdim]edge_bot;')
        if left:
            edge_list.append(f'vector[ydim]edge_left;')
        if right:
            edge_list.append(f'vector[ydim]edge_right;')

        edge_definitions = '\n'.join(edge_list)
    else:
        edge_definitions = ''

    data_segment = DATA_SEGMENT_TEMPLATE.format(
        mask=mask,
        known_map=known_map,
        xcoords=xcoords,
        ycoords=ycoords,
        time=time,
        N=N,
        phi_if_defined=phi_if_defined,
        defined_derivatives=defined_derivatives,
        edge_definitions=edge_definitions,
        drift_sd=drift_sd,
        drift_tile_radius=drift_tile_radius,
    )

    return data_segment
        

TRANSFORMED_DATA_SEGMENT_TEMPLATE = """



    // 
    step_size = 1./granularity;
    n_y_tiles = 1 + granularity * (ydim-1);
    n_x_tiles = 1 + granularity * (xdim-1);

    {edge_modifications}

    {kernel_denominators}

"""

def build_transformed_data_segment(options):
    extra_edges = bool(options['existing_edges'])
    # I think I'll avoid using this for ease of programming
    if extra_edges:
        ee = '0'
    else:
        ee = ''

    if options['phi'] or options['estimate_phi']:
        use_phi = True
    else:
        use_phi = False

    pre_deriv_max = (options['degree'] - 1) // 2

    # edge-corrected masks and "known map" (if use_perfect_grid)
    if options['existing_edges']:
        top = 'T' in options['existing_edges']
        bot = 'B' in options['existing_edges']
        left = 'L' in options['existing_edges']
        right = 'R' in options['existing_edges']

        n_vertical = top + bot
        n_horizontal = left + right
    else:
        edge_modifications = ''

    # kernel-transformed denominators
    if options['kernel_opts']:
        lines = []
        for i, opt in enumerate(options['kernel_opts']):
            for degree_prefix in degree_derivative_iter_max(pre_deriv_max + 1):
                varname = f'k{i}_{degree_prefix}'
                line = f'matrix[ydim,xdim] {varname};'
                # get type of kernel
                kernel_initialization = build_kernel_denominator_loop(
                    opt, degree_prefix, varname,i
                )
                lines.append(kernel_initialization)
        kernel_denominators = '\n'.join(lines)
                
    else:
        kernel_denominators = ''

    return TRANSFORMED_DATA_SEGMENT_TEMPLATE.format(
        edge_modifications = edge_modifications,
        kernel_denominators=kernel_denominators,
    )

def build_parameter_segment(options):
    return '[PLACEHOLDER]'

def build_transformed_parameter_segment(options):
    return '[PLACEHOLDER]'

def build_model_segment(options):
    return '[PLACEHOLDER]'

def build_generated_quantities_segment(options):
    return '[PLACEHOLDER]'
