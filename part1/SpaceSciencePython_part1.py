#!/usr/bin/env python
# coding: utf-8

# 

# In[1]:


# Import the SPICE module
import spiceypy


# In[2]:


# We want to determine the position of our home planet with respect from the Sun.
# The datetime shall be set as "today" (midnight). SPICE requires the Ephemeris Time (ET);
# thus, we need to convert a UTC datetime string to ET.

import datetime

# get today's date
date_today = datetime.datetime.today()

# convert the datetime to a string, replacing the time with midnight
date_today = date_today.strftime('%Y-%m-%dT00:00:00')

# convert the utc midnight string to the corresponding ET
et_today_midnight = spiceypy.utc2et(date_today)


# In[3]:


# oh... an errors occured. The error tells us that a so called "kernel" is missing. These kernels store all
# information that are required for time conversion, pointing, position determination etc.
# For this tutorial the Git repository contains already the necessary kernel. We need to load it first
spiceypy.furnsh('../_kernels/lsk/naif0012.tls')


# In[4]:


# Let's re-try our first time conversion command
et_today_midnight = spiceypy.utc2et(date_today)


# In[5]:


# It works! How does the value look like?
print(et_today_midnight)


# In[6]:


# Can we compute now the position and velocity (so called state) of the Earth with respect to the Sun?
# We use the following function to determine the state vector and the so called light time (travel time of the light
# between the Sun and our home planet).
#
# targ : Object that shall be pointed at
# et : The ET of the computation
# ref : The reference frame. Here, it is ECLIPJ2000 (so Medium article)
# obs :  The observer respectively the center of our state vector computation
earth_state_wrt_sun, earth_sun_light_time = spiceypy.spkgeo(targ=399, et=et_today_midnight, ref='ECLIPJ2000', obs=10)


# In[7]:


# An error occured. Again a kernel error. Well, we need to load a so called spk to load positional information:
spiceypy.furnsh('../_kernels/spk/de432s.bsp')


# In[8]:


# Let's re-try the computation again
earth_state_wrt_sun, earth_sun_light_time = spiceypy.spkgeo(targ=399, et=et_today_midnight, ref='ECLIPJ2000', obs=10)


# In[9]:


# The state vector is 6 dimensional: x,y,z in km and the corresponding velocities in km/s
print('State vector of the Earth w.r.t. the Sun for "today" (midnight):\n', earth_state_wrt_sun)


# In[10]:


# The (Euclidean) distance should be around 1 AU. Why "around"? Well the Earth revolves the Sun in a slightly
# non-perfect circle (elliptic orbit). First, we compute the distance in km.
import math
earth_sun_distance = math.sqrt(earth_state_wrt_sun[0]**2.0                              + earth_state_wrt_sun[1]**2.0                              + earth_state_wrt_sun[2]**2.0)


# In[11]:


# Convert the distance in astronomical units (1 AU)
# Instead of searching for the "most recent" value, we use the default value in SPICE. This way, we can easily compare
# our results with the results of others.
earth_sun_distance_au = spiceypy.convrt(earth_sun_distance, 'km', 'AU')

# Cool, it works!
print('Current distance between the Earth and the Sun in AU:', earth_sun_distance_au)


# # Orbital speed of the Earth
# For this, we need the equation to determine the orbital speed. We assume that the Sun's mass is greater than the mass
# of the Earth and we assume that our planet is moving on an almost circular orbit. The orbit velocity $v_{\text{orb}}$ can be approximated with, where $G$ is the gravitational constant and $M$ is the mass of the Sun. $r$ is the distance between the Earth and the Sun.
# \begin{align}
#     v_{\text{orb}}\approx\sqrt{\frac{GM}{r}}
# \end{align}

# In[12]:


# First, we compute orbital speed of the Earth around the Sun
earth_orb_speed_wrt_sun = math.sqrt(earth_state_wrt_sun[3]**2.0                                   + earth_state_wrt_sun[4]**2.0                                   + earth_state_wrt_sun[5]**2.0)

# It's around 30 km/s
print('Current orbital speed of the Earth around the Sun in km/s:', earth_orb_speed_wrt_sun)


# In[13]:


# Now let's compute the theoretical expectation. First, we load a pck file that contain miscellanoeus information,
# the G*M values for different objects

# First, load the kernel
spiceypy.furnsh('../_kernels/pck/gm_de431.tpc')
_, gm_sun = spiceypy.bodvcd(bodyid=10, item='GM', maxn=1)

# Now compute the orbital speed
v_orb_func = lambda gm, r: math.sqrt(gm/r)
earth_orb_speed_wrt_sun_theory = v_orb_func(gm_sun[0], earth_sun_distance)

# Print the result
print('Theoretical orbital speed of the Earth around the Sun in km/s:', earth_orb_speed_wrt_sun_theory)

