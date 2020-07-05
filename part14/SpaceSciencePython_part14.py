# Import standard modules
import datetime

# Import installed modules
import spiceypy
import numpy as np

# Load the SPICE kernel meta file
spiceypy.furnsh('kernel_meta.txt')

#%%

# Get the G*M value of the Sun
_, GM_SUN_PRE = spiceypy.bodvcd(bodyid=10, item='GM', maxn=1)
GM_SUN = GM_SUN_PRE[0]

# Set the G*M value of Jupiter
_, GM_JUPITER_PRE = spiceypy.bodvcd(bodyid=5, item='GM', maxn=1)
GM_JUPITER = GM_JUPITER_PRE[0]

#%%

# Set a sample Ephemeris Time to compute a sample Jupiter state vector and the
# corresponding orbital elements
sample_et = spiceypy.utc2et('2000-001T12:00:00')

# Compute the state vector of Jupiter as seen from the Sun in ECLIPJ2000
JUPITER_STATE, _ = spiceypy.spkgeo(targ=5, \
                                   et=sample_et, \
                                   ref='ECLIPJ2000', \
                                   obs=10)

# Determine the corresponding orbital elements of Jupiter
JUPITER_ORB_ELEM = spiceypy.oscltx(state=JUPITER_STATE, \
                                   et=sample_et, \
                                   mu=GM_SUN)

# Extract the semi-major axis of Jupiter ...
JUPITER_A = JUPITER_ORB_ELEM[-2]

# ... and print the results in AU
print('Semi-major axis of Jupiter in AU: ' \
      f'{spiceypy.convrt(JUPITER_A, inunit="km", outunit="AU")}')
print('\n')

#%%

# Compute the SOI radius of Jupiter
SOI_JUPITER_R = JUPITER_A * (GM_JUPITER/GM_SUN) ** (2.0/5.0) * 1

# Print the SOI's radius
print('SOI of Jupiter in AU: ' \
      f'{spiceypy.convrt(SOI_JUPITER_R, inunit="km", outunit="AU")}')
print('\n')

#%%

# Compute the state vector and the corresponding orbital elements of 67P as
# seen from the Sun

# Create an ET (2004 day 1 is the minimum date-time in the corresponding SPICE
# spk kernel)
sample_et = spiceypy.utc2et('2004-001T00:00:00')

# Compute the state vector of 67P ...
COMET_67P_STATE, _ = spiceypy.spkgeo(targ=1000012, \
                                     et=sample_et, \
                                     ref='ECLIPJ2000', \
                                     obs=10)

# ... and the corresponding orbital elements
COMET_67P_ORB_ELEM = spiceypy.oscelt(state=COMET_67P_STATE, \
                                     et=sample_et, \
                                     mu=GM_SUN)

#%%

# Now we want to determine when 67P enters the SOI of Jupiter. As a starting
# date we set the 1st January 2017 and compute everything back in time
datetime_stamp = datetime.datetime(year=2017, month=1, day=1)

# Our computation will be performed within a while condition (to check whether
# 67P entered the SOI or not); thus we need to set an initial value for the
# while condition. Here: a very large distance between 67P and Jupiter
comet_jup_dist = 10.0**10

# While condition: Compute the following coding part as long as 67P did not
# enter Jupiter's SOI
while comet_jup_dist > SOI_JUPITER_R:

    # Add one hour to the date-time stamp and convert it ot ET
    datetime_stamp = datetime_stamp + datetime.timedelta(hours=1)
    et_stamp = spiceypy.datetime2et(datetime_stamp)

    # Compute the state vector of 67P based on the initial orbital elements
    # (Sun-centric in ECLIPJ2000)
    COMET_67P_STATE_ORB = spiceypy.conics(COMET_67P_ORB_ELEM, et_stamp)

    # Compute Jupiter's state vector in as seen from the Sun
    JUPITER_STATE, _ = spiceypy.spkgeo(targ=5, \
                                       et=et_stamp, \
                                       ref='ECLIPJ2000', \
                                       obs=10)

    # Compute the distance between Jupiter and 67P
    comet_jup_dist = spiceypy.vnorm(JUPITER_STATE[:3]-COMET_67P_STATE_ORB[:3])

#%%

# If the while condition is not fulfilled, 67P crosses Jupiter's SOI! Let's
# take a look when this happened and also let's verify the distance to
# Jupiter:
print(f'67P entering Jupiter\'s SOI: {datetime_stamp.strftime("%Y-%m-%d")}')
print('67P distance to Jupiter at SOI crossing in AU: ' \
      f'{spiceypy.convrt(comet_jup_dist, inunit="km", outunit="AU")}')

#%%

# Transform the state vector of 67P from a Sun-centric system to a Jupiter-
# centric system ...
COMET_67P_STATE_JUP_CNTR = COMET_67P_STATE_ORB - JUPITER_STATE

# ... and compute the corresponding orbital elements. This time, we need the
# G*M value of Jupiter!
COMET_67P_ORB_ELEM_JUP_CNTR = spiceypy.oscelt(state=COMET_67P_STATE_JUP_CNTR, \
                                              et=et_stamp, \
                                              mu=GM_JUPITER)

#%%

# Let's take a look at the perijove. This will tell us at what distance
# 67P will have it's closes encounter with Jupiter
print('Closest distance between 67P and Jupiter in km: ' \
      f'{COMET_67P_ORB_ELEM_JUP_CNTR[0]}')

print('Closest distance between 67P and Jupiter in SOI radius percentage: ' \
      f'{round(COMET_67P_ORB_ELEM_JUP_CNTR[0] / SOI_JUPITER_R, 2) * 100}')

# Not surprisingly, 67P is not bound to Jupiter. The eccentricity in this
# Jupiter-centric computation is larger than 1:
print('67P\'s eccentricity in a Jupiter-centric system: ' \
      f'{COMET_67P_ORB_ELEM_JUP_CNTR[1]}')
print('\n')

#%%

# In an additional while condition we compute the trajectory of 67P within
# Jupiter's SOI until it reaches, again, the SOI border
while comet_jup_dist <= SOI_JUPITER_R:

    # Add one hour to the ET from the last while condition and convert it to
    # ET
    datetime_stamp = datetime_stamp + datetime.timedelta(hours=1)
    et_stamp = spiceypy.datetime2et(datetime_stamp)

    # Compute an ET corresponding Jupiter-centric state vector of 67P
    comet_67p_state_orb_jup_cntr = \
        spiceypy.conics(COMET_67P_ORB_ELEM_JUP_CNTR, et_stamp)

    # Since we compute everything in a Jupiter-centric system, the norm of the
    # state vector is also the distance to Jupiter
    comet_jup_dist = spiceypy.vnorm(comet_67p_state_orb_jup_cntr[:3])

#%%

# When did 67P leave the SOI?
print(f'67P leaving Jupiter\'s SOI: {datetime_stamp.strftime("%Y-%m-%d")}')

#%%

# Now we need to re-transform the Jupiter centric state vector back to a Sun-
# centric one. First, compute the state vector of Jupiter as seen form the Sun
# at the time when 67P leaves the SOI of Jupiter:
JUPITER_STATE, _ = spiceypy.spkgeo(targ=5, et=et_stamp, ref='ECLIPJ2000', \
                                   obs=10)

# A simple vector addition leads to a Sun-centric 67P state vector
COMET_67P_STATE_ORB_AFTER = comet_67p_state_orb_jup_cntr + JUPITER_STATE

#%%

# And now we can compute the state vector after the close encounter with
# Jupiter:
COMET_67P_ORB_ELEM_AFTER = spiceypy.oscelt(state=COMET_67P_STATE_ORB_AFTER, \
                                           et=et_stamp, mu=GM_SUN)

#%%

# Finally, let's plot the differences between the "old" and "new" orbital
# elements
print('Perihelion in AU '\
      'before: ' \
      f'{round(spiceypy.convrt(COMET_67P_ORB_ELEM[0], "km", "AU"), 2)}, ' \
      'after: ' \
      f'{round(spiceypy.convrt(COMET_67P_ORB_ELEM_AFTER[0], "km", "AU"), 2)}')

print('Eccentricity '\
      'before: ' \
      f'{round(COMET_67P_ORB_ELEM[1], 4)}, ' \
      'after: ' \
      f'{round(COMET_67P_ORB_ELEM_AFTER[1], 4)}')

print('Inclination in degrees '\
      'before: ' \
      f'{round(np.degrees(COMET_67P_ORB_ELEM[2]), 2)}, ' \
      'after: ' \
      f'{round(np.degrees(COMET_67P_ORB_ELEM_AFTER[2]), 2)}')

print('Longitude of ascending node in degrees '\
      'before: ' \
      f'{round(np.degrees(COMET_67P_ORB_ELEM[3]), 2)}, ' \
      'after: ' \
      f'{round(np.degrees(COMET_67P_ORB_ELEM_AFTER[3]), 2)}')

print('Argument of perihelion in degrees '\
      'before: ' \
      f'{round(np.degrees(COMET_67P_ORB_ELEM[4]), 2)}, ' \
      'after: ' \
      f'{round(np.degrees(COMET_67P_ORB_ELEM_AFTER[4]), 2)}')
