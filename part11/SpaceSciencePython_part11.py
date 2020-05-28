# Import the standard modules
import sqlite3

# Import installed modules
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

#%%

# Connect to the comet database. This database has been created in tutorial
# part 7, however, due to its small size the database is uploaded on GitHub
con = sqlite3.connect('../_databases/_comets/mpc_comets.db')

# Create a pandas dataframe that contains the perihelion and the absolute
# magnitude
COMETS_DF = pd.read_sql('SELECT PERIHELION_AU, ABSOLUTE_MAGNITUDE' \
                        ' FROM comets_main WHERE ECCENTRICITY < 1', \
                        con)

#%%

# Print some descriptive statistics
print('Descriptive Statistics of the Absolute Magnitude of Comets')
print(f'{COMETS_DF["ABSOLUTE_MAGNITUDE"].describe()}')

#%%

# Define a histogram bins array
BINS_RANGE = np.arange(-2, 22 + 2, 2)

# Let's set a dark background
plt.style.use('dark_background')

# Set a default font size for better readability
plt.rcParams.update({'font.size': 14})

# Create a figure and axis
fig, ax = plt.subplots(figsize=(12, 8))

# Plot a histogram of the absolute magnitude distribution
ax.hist(COMETS_DF['ABSOLUTE_MAGNITUDE'], bins=BINS_RANGE, color='tab:orange', \
        alpha=0.7)

# Set labels for the x and y axes
ax.set_xlabel('Absolute Magnitude')
ax.set_ylabel('Number of Comets')

# Set a grid
ax.grid(axis='both', linestyle='dashed', alpha=0.2)

# Save the figure
plt.savefig('comets_abs_mag_hist.png', dpi=300)

#%%

# The histogram provides a simple overview of the distribution of the
# Absolute Magnitudes ... what does it imply? Are there really, only a few
# smaller comets in the Solar System?

# Let's create a cumulative histogram as a scatter plot for a better
# visibility of possible trends

# Compute a cumulative distribution of the absolute magnitude
ABS_MAG_HIST, BINS_EDGE = np.histogram(COMETS_DF['ABSOLUTE_MAGNITUDE'], \
                                       bins=BINS_RANGE)
CUMUL_HIST = np.cumsum(ABS_MAG_HIST)

# Create a figure and axis
fig, ax = plt.subplots(figsize=(12, 8))

# Create a scatter plot of the cumulative distribution. Consider, to shift the
# bin array by half of the bins' width
ax.scatter(BINS_EDGE[:-1]+1, CUMUL_HIST, color='tab:orange', alpha=0.7, \
           marker='o')

# Set labels for the x and y axes
ax.set_xlabel('Absolute Magnitude')
ax.set_ylabel('Cumulative Number of Comets')

# Set a grid
ax.grid(axis='both', linestyle='dashed', alpha=0.2)

# Save the figure
plt.savefig('comets_abs_mag_cumul_hist.png', dpi=300)

#%%

# The plot ... does not help a lot ... what about a logarithmic scale?

# Create a figure and axis
fig, ax = plt.subplots(figsize=(12, 8))

# Create a scatter plot of the cumulative distribution.
ax.scatter(BINS_EDGE[:-1]+1, CUMUL_HIST, color='tab:orange', alpha=0.7, \
           marker='o')

# Set labels for the x and y axes
ax.set_xlabel('Absolute Magnitude')
ax.set_ylabel('Cumulative Number of Comets')

# Set a grid
ax.grid(axis='both', linestyle='dashed', alpha=0.2)

# Set a logarithmic y axis
ax.set_yscale('log')

plt.savefig('comets_abs_mag_log10cumul_hist.png', dpi=300)

#%%

# The logarithmic plots appears to be promising. Let's assume that we know all
# larger comets; we use the first 5 data points to create a linear regression
# model in semi-log space

# Create two arrays that contain the abs. mag. for the fitting and plotting
# routine
ABS_MAG_FIT = BINS_EDGE[:5]+1
ABS_MAG_PLOT = BINS_EDGE[:-1]+1

# Get the first 5 cumulative results
CUMUL_FIT = CUMUL_HIST[:5]

# Import the linear model from scikit-learn
from sklearn import linear_model
reg = linear_model.LinearRegression()

# Fit the linear regression model with the data
reg.fit(ABS_MAG_FIT.reshape(-1, 1), np.log10(CUMUL_FIT))

# Compute a linear plot for the entire abs. mag. range
CUMULATIVE_ABS_MAG_PRED = reg.predict(ABS_MAG_PLOT.reshape(-1, 1))

#%%

# Create a figure and axis
fig, ax = plt.subplots(figsize=(12, 8))

# Plot the used data points as white dots and ...
ax.scatter(ABS_MAG_FIT, CUMUL_FIT, color='white', alpha=0.7, marker='o', \
           s=100)

# ... plot also the complete data set
ax.scatter(BINS_EDGE[:-1]+1, CUMUL_HIST, color='tab:orange', alpha=0.7, \
           marker='o')

# Plot the linear regression.
ax.plot(ABS_MAG_PLOT, 10**CUMULATIVE_ABS_MAG_PRED, 'w--', alpha=0.7)

# Set labels for the x and y axes as well as a grid
ax.set_xlabel('Absolute Magnitude')
ax.set_ylabel('Cumulative Number of Comets')
ax.grid(axis='both', linestyle='dashed', alpha=0.2)

# Set a log y scale
ax.set_yscale('log')

# Save the figure
plt.savefig('comets_abs_mag_log10cumul_hist_linreg.png', dpi=300)

#%%

# Let's see wether we find a dependency between the perihelion and the abs.
# mag.
fig, ax = plt.subplots(figsize=(12, 8))

# To visualise the relation between abs. mag. and size better, we scale the
# scatter plot dot size w.r.t. to the abs. mag.
# A large abs. mag. corresponds to a small size. First, subtract the values
# by the maximum and subtract 1 (otherwise the largest value will become 0)
comet_size_plot = abs(COMETS_DF['ABSOLUTE_MAGNITUDE'] \
                      - COMETS_DF['ABSOLUTE_MAGNITUDE'].max() - 1)

# Second and third, normalise the results and scale them by a factor of 100
comet_size_plot /= max(comet_size_plot)
comet_size_plot *= 100

# Create a scatter plot of the perihelion vs. the abs. mag. with the marker
# sizing
ax.scatter(COMETS_DF['PERIHELION_AU'], COMETS_DF['ABSOLUTE_MAGNITUDE'], \
           color='white', s=comet_size_plot, alpha=0.3)

# Invert the y axis to create a graph that is similar to the logic of the
# Malmquist Bias shown in the article
ax.invert_yaxis()

# Set labels and a grid
ax.set_xlabel('Perihelion in AU')
ax.set_ylabel('Absolute Magnitude')
ax.grid(axis='both', linestyle='dashed', alpha=0.2)

# Save the figure
plt.savefig('comets_abs_mag_vs_perih.png', dpi=300)
