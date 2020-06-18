# Import standard modules
import sqlite3
from datetime import datetime, timedelta

# Import installed modules
import spiceypy
import numpy as np
import pandas as pd

#%%

# Load the SPICE kernel meta file
spiceypy.furnsh('kernel_meta.txt')

#%%

# Get the G*M value of the Sun
_, GM_SUN_PRE = spiceypy.bodvcd(bodyid=10, item='GM', maxn=1)
GM_SUN = GM_SUN_PRE[0]

#%%

# Connect to the comet database
CON = sqlite3.connect('../_databases/_comets/mpc_comets.db')

# Extract orbit data of the comet C/2019 Y4 (ATLAS)
ATLAS_ORB_EL = pd.read_sql('SELECT NAME, PERIHELION_AU, ' \
                           'ECCENTRICITY, INCLINATION_DEG, ' \
                           'LONG_OF_ASC_NODE_DEG, ARG_OF_PERIH_DEG, ' \
                           'MEAN_ANOMALY_DEG, EPOCH_ET ' \
                           'FROM comets_main ' \
                           'WHERE NAME="C/2019 Y4 (ATLAS)"', CON)

# Convert the perihelion, that is given in AU, to km
ATLAS_ORB_EL.loc[:, 'PERIHELION_KM'] =  \
    ATLAS_ORB_EL['PERIHELION_AU'].apply(lambda x: \
                                        spiceypy.convrt(x, inunit='AU', \
                                                        outunit='km'))

# Convert all angular parameters to radians, since the entries in the database
# are stored in degrees. The for-loop iterates through all column names that
# contain the word "DEG"
for angle_col_name in [col for col in ATLAS_ORB_EL.columns if 'DEG' in col]:
    ATLAS_ORB_EL.loc[:, angle_col_name.replace('DEG', 'RAD')] = \
        np.radians(ATLAS_ORB_EL[angle_col_name])

# Add the G*M value of the Sun
ATLAS_ORB_EL.loc[:, 'SUN_GM'] = GM_SUN

#%%

# Extract all orbital elements / information in a SPICE compatible order (see
# function conics)
ATLAS_SPICE_ORB_EL = ATLAS_ORB_EL[['PERIHELION_KM', 'ECCENTRICITY', \
                                   'INCLINATION_RAD', 'LONG_OF_ASC_NODE_RAD', \
                                   'ARG_OF_PERIH_RAD', 'MEAN_ANOMALY_DEG', \
                                   'EPOCH_ET', 'SUN_GM']].iloc[0].values

#%%

# Set an initial time and end time for the computation procedure
INI_DATETIME = datetime(year=2020, month=5, day=20)
END_DATETIME = datetime(year=2020, month=6, day=10)

# Create an array that covers the initial and end time in 1 hour steps
TIME_ARRAY = np.arange(INI_DATETIME, END_DATETIME, \
                       timedelta(hours=1)).astype(datetime)

#%%

# Set an empty array that will store the distances between the Sun
# and ATLAS
atlas_vecs = []

# Set an empty array that will store the distances between the Sun
# and the Solar Orbiter
solar_orb_vecs = []

# Iterate through the time array (comet ATLAS)
for atlas_time_step in TIME_ARRAY:

    # Compute the ET
    atlas_et = spiceypy.datetime2et(atlas_time_step)

    # Compute the ET corresponding state vector of the comet ATLAS
    atlas_state_vec = spiceypy.conics(ATLAS_SPICE_ORB_EL, atlas_et)

    # Store the position vector
    atlas_vecs.append(atlas_state_vec[:3])

# Iterate through the time array (Solar Orbiter)
for so_time_step in TIME_ARRAY:

    # Compute the ET
    so_et = spiceypy.datetime2et(so_time_step)

    # Compute the state vector of the Solar Orbiter (NAIF ID: -144)
    solar_orb_state_vec, _ = spiceypy.spkgeo(targ=-144, et=so_et, \
                                         ref='ECLIPJ2000', obs=10)

    # Store the position vector
    solar_orb_vecs.append(solar_orb_state_vec[:3])

# Convert the lists that contain the vectors to numpy lists
atlas_vecs = np.array(atlas_vecs)
solar_orb_vecs = np.array(solar_orb_vecs)

#%%

# Minimum distance ATLAS - Sun
MIN_DIST_ATLAS_SUN = np.min(np.linalg.norm(atlas_vecs, axis=1))
print('Minimum distance ATLAS - Sun in AU: ' \
      f'{spiceypy.convrt(MIN_DIST_ATLAS_SUN, "km", "AU")}')

# Minimum distance Solar Orbiter - Sun
MIN_DIST_SOLAR_ORB_SUN = np.min(np.linalg.norm(solar_orb_vecs, axis=1))
print('Minimum distance Solar Orbiter - Sun in AU: ' \
      f'{spiceypy.convrt(MIN_DIST_SOLAR_ORB_SUN, "km", "AU")}')
print('\n')

#%%

# What is the closest approach between both trajectories?
# Compute a matrix that contains all possible distances, using the scipy
# function cdist
import scipy.spatial
MIN_DIST_MATRIX = scipy.spatial.distance.cdist(atlas_vecs, solar_orb_vecs)

# Print the minimum distance
print('Minimum distance between ATLAS and Solar Orbiter in km: ' \
      f'{np.min(np.round(MIN_DIST_MATRIX))}')
print('\n')

#%%

# The timing needs to be correct too! The comet produces ions and creates
# its tail within the spacecraft's trajectory. Thus, the comet needs to pass
# by the minimum distance first

# Determine the distance matrix indices of the closest approach
indices_min = np.where(MIN_DIST_MATRIX == np.min(MIN_DIST_MATRIX))
indices_min = [k.item() for k in indices_min]

# Let's print the indices for
# ATLAS
print(f'Atlas Index of close approach: {indices_min[0]}')

# Solar Orbiter
print(f'Solar Orbiter Index of close approach: {indices_min[1]}')
print('\n')

#%%

# Corresponding times (only a few days apart. Thus, an ion tail could be
# detectable)
print(f'ATLAS closest approach date-time: {TIME_ARRAY[indices_min[0]]}')
print('Solar Orbiter closest approach date-time: ' \
      f'{TIME_ARRAY[indices_min[1]]}')
print('\n')

#%%

# ... but is the ion tail "aiming" towards the trajectory of the spacecraft?
# (at least within a few degrees?)
# Compute the angular distance between the trajectories' closest approach

# Set the closest approach vectors, based on the obtained indices for ATLAS and
# the Solar Orbiter, respectively
VEC_ATLAS_AP = atlas_vecs[indices_min[0]]
VEC_SOLAR_ORB_AP = solar_orb_vecs[indices_min[1]]

# Determine the norm of both closest approach vectors
ATLAS_NORM_AP = spiceypy.vnorm(VEC_ATLAS_AP)
SOLORB_NORM_AP = spiceypy.vnorm(VEC_SOLAR_ORB_AP)

# Compute the dot product
DOT_PRODUCT_AP = np.dot(VEC_ATLAS_AP, VEC_SOLAR_ORB_AP)

# Compute the angle
ANGULAR_DIST_AP = np.degrees(np.arccos((DOT_PRODUCT_AP) \
                                       / (ATLAS_NORM_AP * SOLORB_NORM_AP)))

# Print the angular distance between ATLAS' ion tail direction and the position
# vector of the spacecraft at the closest approach
print('Minimum angular distance between a possible ion tail and the ' \
      'Solar Orbiter\'s trajectory in degrees: ' \
      f'{np.round(ANGULAR_DIST_AP, 2)}')
