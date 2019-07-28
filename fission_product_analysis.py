#!/usr/bin/env python3
# coding=utf-8
"""
Use to compare fission fragment distributions
"""

import sys
import numpy as np
import pandas as pd

# Sets common directory between file paths
if sys.platform == 'win32':
    directory = \
        'C:/Users/Samuel/Dropbox/Physics/Fourth_Year/Project/Code'
elif sys.platform == 'linux':
    directory = \
        '/home/samuel/Dropbox/Physics/Fourth_Year/Project/Code'
else:
    sys.exit('No Directory present for OS')

# GEF file path/location
gef_directory = directory + '/DecayedMassFractions-master/data/fission/'
# GEFY file path/location
gefy_directory = directory + '/GEFY/ENDF'
# ENDF File name
endf_directory = directory + '/ENDF/files.txt'

# TODO convert endf file to df
#def endf_to_df():


def extract_endf_data(file_name, show=False):
    """
    Extract fission yield data

    From ENDF format file, only works for fission yield data returns
    dictionary containing entries for each isotope and energy where the corresponding
    key is (Z+M,E(eV)) (eg. (92238,0.0253) for Uranium 238, induced fission
    neutron energy = 0.0253)

    Function also prints to console a list of isotopes and energies found
    within file.

    Parameters
    ----------
    file_name : str
        name of file to process
    show : bool
        Print to screen file contents or not.
    Returns
    -------
    dic : dict of DataFrame of str
        eg. dic[(Z+M,E)] = DataFrame[fission_yield, floating_point_value,
                                    product_identity,uncertainty_yield]

    """

    with open(file_name) as file:
        data_set = file.readlines()

    data_set = np.array(data_set)

    data_set = np.core.defchararray.replace(data_set, '+', 'E+')
    data_set = np.core.defchararray.replace(data_set, '-', 'E-')

    dic = {}

    print('Data present in; ' + file_name) if show else None
    print('Isotope(ZM)  Energy(eV)') if show else None

    for line in data_set:
        if line[-9:-6] == '451':  # Header lines
            None
        if line[-9:-6] == '454':  # Body lines

            if int(line[-6:]) == 1:
                isotope = int(float(line[:12]))  # Isotope
            elif line[45] == '0':
                energy = float(line[:12])  # Energy
                print(isotope, '      ', energy) if show else None
                dic[(isotope, energy)] = []
            else:

                dic[(isotope, energy)].append(line[:72].split())

    for key in dic:
        dic[key] = [k for j in dic[key] for k in j]

        dic[key] = np.array(dic[key])#.astype(float)

        # TODO Find a better/faster way to convert type for full array.
        #  Until then just convert to float before plotting.
        
        x = np.arange(int(len(dic[key]) / 4))

        dic[key] = {'product_identity': dic[key][x * 4],
                    'floating_point_value': dic[key][x * 4 + 1],
                    'fission_yield': dic[key][x * 4 + 2],
                    'uncertainty_yield': dic[key][x * 4 + 3]}
        
        dic[key] = pd.DataFrame.from_dict(dic[key])
    return dic

# Take endf file, convert to data frame and clean

# TODO convert txt, csv, etc. to same df
#   best way to mange this file?
#   compression, archiving, etc.

# TODO convert standard request to graph and save to file and push to screen


def pi_to_zm(df):
    """
    Convert product identity to proton and mass number


    Parameters
    ----------
    df : DataFrame
        DataFrame containing a column called 'product_identity'

    Returns
    -------
    df : DataFrame
        With columns called 'proton_number' and 'mass_number'

    """
    temp = df['product_identity'].astype(float).astype(int).astype(str)
    df['proton_number'] = temp.str[0:2].astype(float).astype(int)
    df['mass_number'] = temp.str[2:].astype(float).astype(int)
    return df


if __name__ == '__main__':
    
    import matplotlib.pyplot as plt

    dic = extract_endf_data('files.txt', show=False)
    
    data = (dic[(98252, 0.0)])
    data = pi_to_zm(data)

    data = data.sort_values('mass_number')
    
    data['fission_yield'] = data['fission_yield'].astype(float)

    data = data.groupby('mass_number')['fission_yield'].sum().plot(logy=True)
    plt.show()

