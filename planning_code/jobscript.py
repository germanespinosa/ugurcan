import argparse, os, sys
from init import *

if __name__ == "__main__":
    exampleUsage = '''example:
    python main.py --visualrange (-v) [working directory] (entropy 0, visual range limited simulations)
    python main.py --visualrange (-v) --entropy (-e) [working directory] (mid-entropy visual range limited simulations)
    python main.py --verbose (-x) [working directory] (entropy 0, visual range unlimited simulations, verbose)'''

    parser = argparse.ArgumentParser(prog='main.py',
                                     description="Define simulation type",
                                     epilog=exampleUsage)

    # THESE OPTION MIRROR BASH SCRIPT OPTIONS
    parser.add_argument('outdir', type=str, help='Output directory')
    parser.add_argument('-v', '--visualrange', action='store_true',
                        help='Specify whether the simulation is visual range defined. Default: '
                             '0 (Fig1 parameters)')
    parser.add_argument('-e', '--entropy', action='store_true',
                        help='Specify whether the simulation is in a cluttered environment ('
                             'pre-loaded). Default: 0 (Fig1 parameters)')
    parser.add_argument('-x', '--verbose', action='store_true', help='Specify verbosity. Default not verbose')

    namespace = parser.parse_args()

    ###################################################################################################################




    print(namespace.visualrange)
