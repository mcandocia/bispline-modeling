import argparse
import logging
import os
import re
from sympy import symbols, expand, integrate, diff, solve

# type checks for parser
from checks import *

from segments import build_data_segment
from segments import build_transformed_data_segment
from segments import build_parameter_segment
from segments import build_transformed_parameter_segment
from segments import build_model_segment
from segments import build_generated_quantities_segment

TEMPLATE_LOCATION = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'templates'
)

BASE_TEMPLATE_FN = 'base_template.stan'

def get_options():
    parser = argparse.ArgumentParser(
        description='Build a Stan file for fitting 2D splines to surfaces.'
    )
    parser.add_argument(
        'filename',
        default='',
        help='Output Filename. If empty, one will be generated from parameters'
    )

    parser.add_argument(
        '--directory',
        help='Output directory',
        default='.'
    )

    parser.add_argument(
        '--degree',
        help='Degree of splines. Must be odd integer.',
        type=check_odd,
        required=True
    )

    parser.add_argument(
        '--estimate-phi',
        action='store_true',
        help='Estimate phi'
    )

    parser.add_argument(
        '--phi',
        type=check_real_under_1,
        help='Initial estimate of phi. If this and --estimate-phi are not specified, time drift is not assumed.'
    )

    parser.add_argument(
        '--derivative-penalties',
        nargs='*',
        required=False,
        help='Derivatives of spline which will have penalty terms of their squared norms.',
        type=check_whole,
        default=[1]
    )

    parser.add_argument(
        '--use-perfect-grid',
        action='store_true',
        help='Input data will be expected to fit grid which defines endpoints of splines'
    )

    parser.add_argument(
        '--sample-data-tile-radius',
        help='Maximum number of tiles away (in L0 norm) drifted xy values can be from their "center". Not compatible with `--use-perfect-grid`.',
        type=check_whole,
        default=0
    )

    parser.add_argument(
        '-v','--verbose',
        dest='verbose',
        action='store_true',
        help='Print out extra detail during script'
    )

    parser.add_argument(
        '--kernel-opts',
        nargs='*',
        help="Comma'd tuples in the form of (D,R,T), where D is spacing distance, R is rate of decay, and T is type. T=0 is square (pyramid), T=1 is diamond (pyramid), T=2 is normal kernel. Can also be in form of (D,R,T,dflag,max_range,normal_sd) for more control.",
        type=check_kernel
    )

    parser.add_argument(
        '--existing-edges',
        nargs='*',
        choices=['T','B','L','R'],
        help = 'Indicates which sides of the map will be provided as input. T=top (y=0), B=bottom, L=left (x=0) R=right. T^his creates a total of 2^4=16 different configurations for the model. Note that corners will overlap, but the top/bottom values are the ones that are used.'
    )

    parser.add_argument(
        '--drift-sd',
        type=check_sd,
        default=0,
        help='Drift standard deviation. If nonzero, will assume x-y drift in model'
    )

    args = parser.parse_args()
    options = vars(args)
    # last validity check
    if not options['filename']:
        options['filename'] = 'bispline_D{degree}E{edges}K{kernels}DP{dpenalty}_{pgrid}.stan'.format(
            degree = options['degree'],
            edges = ''.join(options['existing_edges']),
            kernels = '_'.join(['-'.join(e) for e in options['kernel_opts']]),
            dpenalty = '-'.join(options['derivative_penalties']),
            pgrid = ['PG','CS%s' % options['sample_data_tile_radius']][1 - options['use_perfect_grid']]
        )

    if options['use_perfect_grid'] and (options['drift_sd'] > 0 or options['use_phi']):
        raise argparse.ArgumentTypeError(
            'Cannot enable --use-perfect-grid and define `drift_sd` or enable --use-phi'
        )

    # build logger and incorporate verbose arg
    
    # return
    return options
        

def build_stan(options):
    data_segment = build_data_segment(options)
    transformed_data_segment = build_transformed_data_segment(options)
    parameter_segment = build_parameter_segment(options)
    transformed_parameter_segment = build_transformed_parameter_segment(options)
    model_segment = build_model_segment(options)
    generated_quantities_segment = build_generated_quantities_segment(options)


    with open(os.path.join(TEMPLATE_LOCATION,BASE_TEMPLATE_FN),'r') as f:
        base_template = f.read()

    stan_file = base_template.format(
        data_template=data_segment,
        transformed_data_template=transformed_data_segment,
        parameters_template=parameter_segment,
        transformed_parameters_template=transformed_parameter_segment,
        model_template=model_segment,
        generated_quantities_template=generated_quantities_segment
    )

    output_fn = os.path.join(
        options['directory'],
        options['filename']
    )

    with open(output_fn,'w') as f:
        f.write(stan_file)
        


if __name__=='__main__':
    options = get_options()
    build_stan(options)
