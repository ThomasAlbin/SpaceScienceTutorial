# Import the standard modules
import datetime
import pathlib
import sqlite3

# Import installed modules
import pandas as pd
import numpy as np
import spiceypy

# Import the Python script func from the auxiliary folder
import sys
sys.path.insert(1, '../_auxiliary')
import func

#%%

# Set a local download path and the URL to the comet data from the Minor
# Planet Center
DL_PATH = 'raw_data/'
DL_URL = 'https://www.minorplanetcenter.net/Extended_Files/cometels.json.gz'

# Download the comet data and store them in the directory
func.download_file(DL_PATH, DL_URL)

#%%

# Load the SPICE kernel meta file
spiceypy.furnsh('kernel_meta.txt')

#%%

# Read the g-zipped json file with pandas read_json. The function allows one
# to read compressed data
c_df = pd.read_json('raw_data/cometels.json.gz', compression='gzip')

#%%

# First we parse the date and time information. The dataset contains two
# time related information: the date-time of the last perihelion passage and
# another variable called Epoch. However, "epoch" is not related to the mean
# anomaly related epoch and represents other time information in this case.
#
# For our "actual" Epoch case we need to create a UTC time string based on the
# date and time of the last perihelion passage (the time corresponds to a mean
# anomaly of 0 degrees). The Day is given in DAY.FRACTION_OF_DAY. We extract
# only the day
c_df.loc[:, 'EPOCH_UTC_DATE'] = \
    c_df.apply(lambda x: str(x['Year_of_perihelion']) + '-' \
                         + str(x['Month_of_perihelion']) + '-' \
                         + str(x['Day_of_perihelion']).split('.')[0], \
               axis=1)

# Now we need to parse the .FRACTION_OF_DAY given between (0.0, 1.0). First,
# create a place-holder date
PRE_TIME = datetime.datetime(year=2000, month=1, day=1)

# Use the pre_time date-time object and add the days and fraction of days with
# the timedelta function from the datetime library. Extract only the time
# substring ...
c_df.loc[:, 'EPOCH_UTC_TIME'] = \
    c_df['Day_of_perihelion'] \
        .apply(lambda x: (PRE_TIME + datetime.timedelta(days=x)).\
                                                          strftime('%H:%M:%S'))

# ... and based with the date, create now the UTC date-time
c_df.loc[:, 'EPOCH_UTC'] = c_df.apply(lambda x: x['EPOCH_UTC_DATE'] \
                                                + 'T' \
                                                + x['EPOCH_UTC_TIME'],\
                                      axis=1)

# Convert the UTC datetime to ET
c_df.loc[:, 'EPOCH_ET'] = c_df['EPOCH_UTC'].apply(lambda x: spiceypy.utc2et(x))

#%%

# Let's compute a state vector of the comet Hale-Bopp as an example

# Extract the G*M value of the Sun and assign it to a constant
_, GM_SUN_PRE = spiceypy.bodvcd(bodyid=10, item='GM', maxn=1)
GM_SUN = GM_SUN_PRE[0]

# Get the Hale-Bopp data
HALE_BOPP_DF = c_df.loc[c_df['Designation_and_name'].str.contains('Hale-Bopp')]

# Set an array with orbital elements in a required format for the conics
# function. Note: the mean anomaly is 0 degrees and will be set as a default
# value in the SQLite database
HALE_BOPP_ORB_ELEM = [spiceypy.convrt(HALE_BOPP_DF['Perihelion_dist'] \
                                      .iloc[0], 'AU', 'km'), \
                      HALE_BOPP_DF['e'].iloc[0], \
                      np.radians(HALE_BOPP_DF['i'].iloc[0]), \
                      np.radians(HALE_BOPP_DF['Node'].iloc[0]), \
                      np.radians(HALE_BOPP_DF['Peri'].iloc[0]), \
                      0.0, \
                      HALE_BOPP_DF['EPOCH_ET'].iloc[0], \
                      GM_SUN]

#%%

# Compute the state vector for midnight 2020-05-10
HALE_BOPP_ST_VEC = spiceypy.conics(HALE_BOPP_ORB_ELEM, \
                                   spiceypy.utc2et('2020-05-10'))

# Compare with results from https://ssd.jpl.nasa.gov/horizons.cgi
print('Comparison of the computed state \n' \
      'vector with the NASA HORIZONS results')
print('==========================================')
print(f'X in km (Comp): {HALE_BOPP_ST_VEC[0]:e}')
print('X in km (NASA): 5.348377806424425E+08')
print('==========================================')
print(f'Y in km (Comp): {HALE_BOPP_ST_VEC[1]:e}')
print('Y in km (NASA): -2.702225247057124E+09')
print('==========================================')
print(f'Z in km (Comp): {HALE_BOPP_ST_VEC[2]:e}')
print('Z in km (NASA): -5.904425343521862E+09')
print('==========================================')
print(f'VX in km/s (Comp): {HALE_BOPP_ST_VEC[3]:e}')
print('VX in km/s (NASA): 6.857065492623227E-01')
print('==========================================')
print(f'VY in km/s (Comp): {HALE_BOPP_ST_VEC[4]:e}')
print('VY in km/s (NASA): -3.265390887669909E+00')
print('==========================================')
print(f'VZ in km/s (Comp): {HALE_BOPP_ST_VEC[5]:e}')
print('VZ in km/s (NASA): -3.265390887669909E+00')

#%%

# Compute the semi-major axis for closed orbits ...
c_df.loc[:, 'SEMI_MAJOR_AXIS_AU'] = \
    c_df.apply(lambda x: x['Perihelion_dist'] / (1.0 - x['e']) if x['e'] < 1 \
                         else np.nan, \
               axis=1)

# ... as well as the APHELION (if applicable)
c_df.loc[:, 'APHELION_AU'] = \
    c_df.apply(lambda x: (1.0 + x['e']) * x['SEMI_MAJOR_AXIS_AU'] \
                         if x['e'] < 1 else np.nan, \
               axis=1)

#%%

# Create a sub-directory in the main directory of this repository, where a
# comet database shall be stored
pathlib.Path('../_databases/_comets/').mkdir(parents=True, exist_ok=True)

# Create / Connect to a comet database and set the cursor
con = sqlite3.connect('../_databases/_comets/mpc_comets.db')
cur = con.cursor()

# Create (if not existing) a comets' main table, where miscellaneous
# parameters are stored
cur.execute('CREATE TABLE IF NOT EXISTS ' \
            'comets_main(NAME TEXT PRIMARY KEY, ' \
                        'ORBIT_TYPE TEXT, ' \
                        'PERIHELION_AU REAL, ' \
                        'SEMI_MAJOR_AXIS_AU REAL, ' \
                        'APHELION_AU REAL, ' \
                        'ECCENTRICITY, ' \
                        'INCLINATION_DEG REAL, ' \
                        'ARG_OF_PERIH_DEG REAL, ' \
                        'LONG_OF_ASC_NODE_DEG REAL, ' \
                        'MEAN_ANOMALY_DEG REAL DEFAULT 0.0, ' \
                        'EPOCH_UTC TEXT, ' \
                        'EPOCH_ET REAL, ' \
                        'ABSOLUTE_MAGNITUDE REAL, ' \
                        'SLOPE_PARAMETER REAL'
                        ')')

#%%

# Insert the data
cur.executemany('INSERT OR REPLACE INTO ' \
                'comets_main(NAME, ' \
                            'ORBIT_TYPE, ' \
                            'PERIHELION_AU, ' \
                            'SEMI_MAJOR_AXIS_AU, ' \
                            'APHELION_AU, ' \
                            'ECCENTRICITY, ' \
                            'INCLINATION_DEG, ' \
                            'ARG_OF_PERIH_DEG, ' \
                            'LONG_OF_ASC_NODE_DEG, ' \
                            'EPOCH_UTC, ' \
                            'EPOCH_ET, ' \
                            'ABSOLUTE_MAGNITUDE, ' \
                            'SLOPE_PARAMETER'
                            ') ' \
                'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', \
                c_df[['Designation_and_name', \
                      'Orbit_type', \
                      'Perihelion_dist', \
                      'SEMI_MAJOR_AXIS_AU', \
                      'APHELION_AU', \
                      'e', \
                      'i', \
                      'Peri', \
                      'Node', \
                      'EPOCH_UTC', \
                      'EPOCH_ET', \
                      'H', \
                      'G']].values)

# Commit
con.commit()

# Close the database. The database shall be the fundament for the next
# tutorial sessions
con.close()
