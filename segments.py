import re

from tools import clns

from tools import degree_derivative_iter_max
from tools import degree_derivative_iter_sum

from subsegments import initialize_kernel
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
        mask = f'mask = matrix[ydim,xdim]'
        known_map = f'known_map = matrix[ydim,xdim]'
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

    degree = options['degree']
    required_derivative_names = degree_derivative_iter_max(degree // 2)        

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
        for name in required_derivative_names:
            if top:
                edge_list.append(f'row_vector[xdim]edge_top_{name};')
            if bot:
                edge_list.append(f'row_vector[xdim]edge_bot_{name};')
            if left:
                edge_list.append(f'vector[ydim]edge_left_{name};')
            if right:
                edge_list.append(f'vector[ydim]edge_right_{name};')

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

PARAMETER_TEMPLATE = """
// parameter grid w/necessary truncations for each derivative
// if kernels used, rename this with `_raw` 
{parameter_grid_definitions}

// kernel matrices
{kernel_definitions}

//  if z-drift is being used, define the errors and the sigmas
//  (also allow sigmas to be defined)
{zdrift_definitions}

//  if xy-drift is being used, define matrix of drifts
//  sigma should be defined in `data` block, not here
{xydrift_definitions}

// future: define additional variates used in model

"""

def build_parameter_segment(options):
    degree = options['degree']
    # determine # of top and bottom portions of grid that are sliced off
    if options['existing_edges'] or options['kernel_opts']:
        if options['existing_edges']:
            top = 'T' in options['existing_edges']
            bot = 'B' in options['existing_edges']
            left = 'L' in options['existing_edges']
            right = 'R' in options['existing_edges']
        else:
            top = False
            bot = False
            left = False
            right = False
        n_vertical = top + bot
        n_horizontal = left + right            
        sfx = '_raw'
    else:
        n_vertical = 0
        n_horizontal = 0
        sfx = ''

    required_derivative_names = degree_derivative_iter_max(degree // 2)
    grid_definition_list = []
    for name in required_derivative_names:
        grid_definition_list.append(
            f'matrix[ydim-{n_vertical},xdim-{n_horizontal}] map{sfx}_{name};'
        )

    parameter_grid_definitions = '\n'.join(grid_definition_list)

    if options['kernel_opts']:
        lines = []
        for i, opt in enumerate(options['kernel_opts']):
            lines.append(initialize_kernel(opt,i))
        kernel_definitions = '\n'.join(lines)
            
    else:
        kernel_definitions = ''

    # z-drift
    if options['phi'] or options['estimate_phi']:
        use_phi = True
    else:
        use_phi = False

    if use_phi:
        zdrift_definitions = clns("""
        // z-drift
        vector[N] e_zdrift;
        real e_zdrift0;
        // time delta
        vector[N] td;
        """)
    else:
        zdrift_definitions = ''

    # xy-drift
    if options['drift_sd']:
        xydrift_definitions = clns("""
        vector[N] xdrift;
        vector[N] ydrift;
        real xdrift0;
        real ydrift0;
        """)
    else:
        xydrift_definitions = ''

    parameter_segment = PARAMETER_TEMPLATE.format(
        parameter_grid_definitions=parameter_grid_definitions,
        kernel_definitions = kernel_definitions,
        zdrift_definitions = zdrift_definitions,
        xydrift_definitions = xydrift_definitions,
    )

    return parameter_segment
    

TRANSFORMED_PARAMETER_TEMPLATE = """
// append edges to parameters for each derivative (if applicable)
// also defines non-raw matrix if kernels are used
{edge_appends}

// calculate kernel contributions (if applicable)
{kernel_contributions}

// calculate sub-blocks for each derivative {{00,01,10,11}}
{subblock_definitions}

// calculate a-values for spline
{a_values}

// calculate squared derivatives used for penalties
{squared_derivatives}

// if z-drift is being used, define cumulative error with time drift component
{zdrift_error}

// if xy-drift is being used, calcualte probabilities of transitions
{xydrift_error}

// calculate the estimates for each point
// if xy-drift is allowed, first determine the cell 
// future: include effects of variates in the model
{estimates_calculation}

// calculate overall penalty
{penalty_calculation}

"""

def build_transformed_parameter_segment(options):
    degree = options['degree']
    required_derivative_names = degree_derivative_iter_max(degree // 2)
    
    if options['existing_edges'] or options['kernel_opts']:
        if options['existing_edges']:
            top = 'T' in options['existing_edges']
            bot = 'B' in options['existing_edges']
            left = 'L' in options['existing_edges']
            right = 'R' in options['existing_edges']
        else:
            top = False
            bot = False
            left = False
            right = False
            
        n_vertical = top + bot
        n_horizontal = left + right

        # loop with appends
        lines = []
        for name in required_derivative_names:
            base_name = f'map_{name}'
            raw_name = f'{base_name}_raw'
            lines.append(
                f'matrix[ydim,xdim] {base_name};'
            )
            if top:
                vname = f'edge_top_{name}'
                top_append = clns(f"""
                for (i in 1:xdim){{
                {base_name}[1,i] = {vname}[i];
                }}
                """)
                tb = '2'
                lines.append(top_append)
            else:
                tb = '1'
            if bot:
                vname = f'edge_bot_{name}'
                bot_append = clns(f"""
                for (i in 1:xdim){{
                {base_name}[ydim,i] = {vname}[i];
                }}
                """)
                bb = 'ydim-1'
                lines.append(bot_append)
            else:
                bb = 'ydim'
            if left:
                vname = f'edge_left_{name}'
                bot_append = clns(f"""
                for (i in 1:ydim){{
                {base_name}[i,1] = {vname}[i];
                }}
                """)
                lines.append(left_append)
                lb = '2'
            else:
                lb = '1'
                
            if right:
                vname = f'edge_right_{name}'
                bot_append = clns(f"""
                for (i in 1:ydim){{
                {base_name}[i,xdim] = {vname}[i];
                }}
                """)
                lines.append(right_append)
                rb = 'xdim-1'
            else:
                rb='xdim'
            # center matrix
            center_assignment = "{base_name}[{tb}:{bb},{lb}:{rb}] = {raw_name};"
            lines.append(center_assignment)
        edge_appends = '\n'.join(lines)

    else:
        n_vertical = 0
        n_horizontal = 0
        edge_appends = ''

    # kernel contributions
    if options['kernel_opts']:
        lines = []
        for degree_prefix in required_derivative_names:
            for i, opt in enumerate(options['kernel_opts']):
                varname = f'k{i}_{degree_prefix}'
                lines.append(build_kernel_loop(
                    opt,
                    options,
                    degree_prefix,
                    varname,
                    i
                ))
        kernel_contributions = '\n'.join(lines)
            
    else:
        kernel_contributions = ''

        
    if options['phi'] or options['estimate_phi']:
        use_phi = True
    else:
        use_phi = False

    if use_phi:
        zdrift_error = '[PLACEHOLDER]'
    else:
        zdrift_definitions = ''

    # xy-drift
    if options['drift_sd']:
        xydrift_error = '[PLACEHOLDER]'
    else:
        xydrift_error = ''

MODEL_TEMPLATE = """
// to help stabilize parameters
// will not be particularly strong
{kernel_priors}
{derivative_priors}

target+=-penalty;

"""

def build_model_segment(options):
    return '[PLACEHOLDER]'


GENERATED_QUANTITIES_TEMPLATE = """
// z-drift estimate (if applicable)

// granular maps for each set of derivatives

"""

def build_generated_quantities_segment(options):
    return '[PLACEHOLDER]'
