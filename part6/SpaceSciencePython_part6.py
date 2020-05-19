# Import the modules
import datetime
import pathlib
import urllib.request
import os

import numpy as np
import spiceypy

#%%

# We define a function that is useful for downloading SPICE
# kernel files. Some kernels are large and cannot be uploaded on the GitHub
# repository. Thus, this helper function shall support you for future kernel
# management (if needed).
def download_kernel(dl_path, dl_url):
    """
    download_kernel(DL_PATH, DL_URL)

    This helper function supports one to download kernel files from the NASA
    NAIF repository and stores them in the _kernel directory.

    Parameters
    ----------
    DL_PATH : str
        Download path on the local machine, relative to this function.
    DL_URL : str
        Download url of the requested kernel file.
    """

    # Obtain the kernel file name from the url string. The url is split at
    # the "/", thus the very last entry of the resulting list is the file's
    # name
    file_name = dl_url.split('/')[-1]

    # Create necessary sub-directories in the DL_PATH direction (if not
    # existing)
    pathlib.Path(dl_path).mkdir(exist_ok=True)

    # If the file is not present in the download directory -> download it
    if not os.path.isfile(dl_path + file_name):

        # Download the file with the urllib  package
        urllib.request.urlretrieve(dl_url, dl_path + file_name)

#%%

# Download the asteroids spk kernel file. First, set a download path, then
# the url and call the download function
PATH = '../_kernels/spk/'
URL = 'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/asteroids/' \
      + 'codes_300ast_20100725.bsp'

download_kernel(PATH, URL)

# Download an auxiliary file from the repository that contains the NAIF ID
# codes and a reference frame kernel that is needed. Since we have a mixture
# of different kernel types we store the data in a sub-directory called _misc
PATH = '../_kernels/_misc/'
URL = 'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/asteroids/' \
      + 'codes_300ast_20100725.tf'

download_kernel(PATH, URL)

#%%

# Load the SPICE kernels via a meta file
spiceypy.furnsh('kernel_meta.txt')

# Create an initial date-time object that is converted to a string
DATETIME_UTC = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

# Convert to Ephemeris Time (ET) using the SPICE function utc2et
DATETIME_ET = spiceypy.utc2et(DATETIME_UTC)

#%%

# ECLIPJ2000_DE405 and ECLIPJ2000 appear to be similar?! A transformation
# matrix between both coordinate systems (for state vectors) should be
# consequently the identity matrix
MAT = spiceypy.sxform(instring='ECLIPJ2000_DE405', \
                      tostring='ECLIPJ2000', \
                      et=DATETIME_ET)

# Let's print the transformation matrix row-wise (spoiler alert: it is the
# identity matrix)
print('Transformation matrix between ECLIPJ2000_DE405 and ECLIPJ2000')
for mat_row in MAT:
    print(f'{np.round(mat_row, 2)}')
print('\n')

#%%

# Compute the state vector of Ceres in ECLIPJ2000 as seen from the Sun
CERES_STATE_VECTOR, _ = spiceypy.spkgeo(targ=2000001, \
                                        et=DATETIME_ET, \
                                        ref='ECLIPJ2000',
                                        obs=10)

#%%

# Get the G*M value for the Sun
_, GM_SUN_PRE = spiceypy.bodvcd(bodyid=10, item='GM', maxn=1)

GM_SUN = GM_SUN_PRE[0]

#%%

# Compute the orbital elements of Ceres using the computed state vector
CERES_ORBITAL_ELEMENTS = spiceypy.oscltx(state=CERES_STATE_VECTOR, \
                                         et=DATETIME_ET, \
                                         mu=GM_SUN)

# Set and convert the semi-major axis and perihelion from km to AU
CERES_SEMI_MAJOR_AU = spiceypy.convrt(CERES_ORBITAL_ELEMENTS[9], \
                                      inunit='km', outunit='AU')
CERES_PERIHELION_AU = spiceypy.convrt(CERES_ORBITAL_ELEMENTS[0], \
                                      inunit='km', outunit='AU')

# Set the eccentricity
CERES_ECC = CERES_ORBITAL_ELEMENTS[1]

# Set and convert miscellaneous angular values from radians to degrees:
# inc: Inclination
# lnode: Longitude of ascending node
# argp: Argument of perihelion
CERES_INC_DEG = np.degrees(CERES_ORBITAL_ELEMENTS[2])
CERES_LNODE_DEG = np.degrees(CERES_ORBITAL_ELEMENTS[3])
CERES_ARGP_DEG = np.degrees(CERES_ORBITAL_ELEMENTS[4])

# Set the orbit period. Convert from seconds to years
CERES_ORB_TIME_YEARS = CERES_ORBITAL_ELEMENTS[10] / (86400.0 * 365.0)

#%%

# Compare the results with the data from the Minor Planet Center
# https://www.minorplanetcenter.net/dwarf_planets

# Print the results next to the MPC results
print('Ceres\' Orbital Elements')
print(f'Semi-major axis in AU: {round(CERES_SEMI_MAJOR_AU, 2)} (MPC: 2.77)')
print(f'Perihelion in AU: {round(CERES_PERIHELION_AU, 2)} (MPC: 2.56)')

print(f'Eccentricity: {round(CERES_ECC, 2)} (MPC: 0.08)')

print(f'Inclination in degrees: {round(CERES_INC_DEG, 1)} (MPC: 10.6)')
print(f'Long. of. asc. node in degrees: {round(CERES_LNODE_DEG, 1)} ' \
      '(MPC: 80.3)')
print(f'Argument of perih. in degrees: {round(CERES_ARGP_DEG, 1)} ' \
      '(MPC: 73.6)')

print(f'Orbit period in years: {round(CERES_ORB_TIME_YEARS, 2)} ' \
      '(MPC: 4.61)')
print('\n')

#%%

# Convert the orbital elements back to the state vector
CERES_STATE_RE = spiceypy.conics([CERES_ORBITAL_ELEMENTS[0], \
                                  CERES_ORBITAL_ELEMENTS[1], \
                                  CERES_ORBITAL_ELEMENTS[2], \
                                  CERES_ORBITAL_ELEMENTS[3], \
                                  CERES_ORBITAL_ELEMENTS[4], \
                                  CERES_ORBITAL_ELEMENTS[5], \
                                  CERES_ORBITAL_ELEMENTS[6], \
                                  GM_SUN], DATETIME_ET)

print('State vector of Ceres from the kernel:\n' \
      f'{CERES_STATE_VECTOR}')
print('State vector of Ceres based on the determined orbital elements:\n' \
      f'{CERES_STATE_RE}')
print('\n')

#%%

# On spaceweather.com we can see that an asteroid has a close Earth fly-by:
# 136795(1997BQ) on 2020-May-21 at a distance of 16.1 Lunar Distance
#
# Will the encounter alter the orbit of the asteroid? Let's have a first look
# on the so-called sphere of influence (SOI) of our planet.
# A simple model assumes that the SOI is a sphere. The semi major axis is set
# to 1 AU:

# 1 AU in km
ONE_AU = spiceypy.convrt(x=1, inunit='AU', outunit='km')

# Set the G*M parameter of our planet
_, GM_EARTH_PRE = spiceypy.bodvcd(bodyid=399, item='GM', maxn=1)
GM_EARTH = GM_EARTH_PRE[0]

# Compute the SOI radius of the Earth
SOI_EARTH_R = ONE_AU * (GM_EARTH/GM_SUN) ** (2.0/5.0)

# Set one Lunar Distance (LD) in km (value from spaceweather.com)
ONE_LD = 384401.0

print(f'SOI of the Earth in LD: {SOI_EARTH_R/ONE_LD}')
print('\n')

#%%

# Now we can compute the current position of the object. We obtain the orbit
# elements data from https://ssd.jpl.nasa.gov/sbdb.cgi?sstr=136795

# Before we compute a state vector of the asteroid and the current distance
# to our home planet we need to define a function to round the data. A common
# convention for scientific work is to round the data to two significant
# digits. We create a lambda function that rounds the values based on the
# provided measurement error
round_sig = lambda value, err: np.round(value, \
                                        -1*(int(np.floor(np.log10(err))))+1)

#%%

# Set now the perihelion in km
NEO_1997BQ_PERIHELION_KM = spiceypy.convrt(round_sig(0.9109776989775201, \
                                                     9.5537e-08), \
                                           inunit='AU', outunit='km')

# Set the eccentricity
NEO_1997BQ_ECC = round_sig(0.4786097161397527, 5.364e-08)

# Set the inclination, longitude of ascending node and argument of periapsis
# in radians
NEO_1997BQ_INC_RAD = np.radians(round_sig(10.99171566990081, 7.6286e-06))
NEO_1997BQ_LNODE_RAD = np.radians(round_sig(50.19104637224941, 3.6206e-05))
NEO_1997BQ_ARGP_RAD = np.radians(round_sig(147.4553849006326, 3.6033e-05))

# Set the mean anomaly and corresponding epoch in Julian Date (JD)
NEO_1997BQ_M0_AT_T0_RAD = np.radians(round_sig(17.87249899172771, 1.0297e-05))
NEO_1997BQ_T0 = spiceypy.utc2et('2459000.5 JD')

#%%

# Set the orbital elements array
NEO_1997BQ_ORBITAL_ELEMENTS = [NEO_1997BQ_PERIHELION_KM, \
                               NEO_1997BQ_ECC, \
                               NEO_1997BQ_INC_RAD, \
                               NEO_1997BQ_LNODE_RAD, \
                               NEO_1997BQ_ARGP_RAD, \
                               NEO_1997BQ_M0_AT_T0_RAD, \
                               NEO_1997BQ_T0, \
                               GM_SUN]

# Compute the state vector
NEO_1997BQ_STATE_VECTOR = spiceypy.conics(NEO_1997BQ_ORBITAL_ELEMENTS, DATETIME_ET)

print(f'Current state vector of 1997BQ in km and km/s ({DATETIME_UTC})):\n' \
      f'{NEO_1997BQ_STATE_VECTOR}')
print('\n')

#%%

# Now compute the state vector of the Earth:
EARTH_STATE_VECTOR, _ = spiceypy.spkgeo(targ=399, \
                                        et=DATETIME_ET, \
                                        ref='ECLIPJ2000',
                                        obs=10)

# Compute the current distance of the Earth and the asteroids in LD
EARTH_1997BQ_DIST_KM = spiceypy.vnorm(EARTH_STATE_VECTOR[:3] \
                                      - NEO_1997BQ_STATE_VECTOR[:3])
print(f'Current distance between the Earth and 1997BQ ({DATETIME_UTC}):\n' \
      f'{EARTH_1997BQ_DIST_KM / ONE_LD} LDe')
