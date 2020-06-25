# Import modules
import pandas as pd
import numpy as np

# Create an empty dataframe lookup table
mag_lookup_df = pd.DataFrame([])

#%%

# Function that converts magnitude to irradiance in W/m^2
def mag2irr(mag, use_attn=False):
    """
    This function converts the apparent magnitude to the corresponding
    irradiance value given in [W/m^2].

    Parameters
    ----------
    mag : float
        The astronomical magnitude.
    use_attn : bool, optional
        Boolean value. If True, a constant factor will be applied that
        represents a simple atmospheric attenuation. The default is False.

    Returns
    -------
    irr : float
        The resulting irradiance given in [W/m^2].
    """

    # If the user wants the atmospheric attenuation, a constant value of 0.4
    # is set ...
    if use_attn:
        attn = 0.4

    # ... otherwise a value of 0 is set
    else:
        attn = 0.0

    # Compute the irradiance
    irr = 10.0 ** (0.4 * (-mag - 19.0 + attn))

    # Return the irradiance
    return irr

#%%

# Function that converts the irradiance to power given in W
def irr2pwr(irr, area):
    """
    This function converts the irradiance given in [W/m^2] to the power [W]
    for a user defined area given in [m^2]

    Parameters
    ----------
    irr : float
        The irradiance given in [W/m^2].
    area : float
        The area given in [m^2].

    Returns
    -------
    pwr : float
        The resulting power given in [W].
    """
    pwr = irr * area

    return pwr

#%%

# Function that converts the power given in [W] to energy given in [J]
def pwr2enr(pwr, time):
    """
    This function converts the power given in [W] to the corresponding energy
    [J], depending on the input time given in [s]

    Parameters
    ----------
    pwr : float
        The power given in [W].
    time : float
        The time given in [s].

    Returns
    -------
    enr : float
        The energy given in [J].
    """

    # Compute the energy
    enr = pwr * time

    # Return the energy
    return enr

#%%

# Set a magnitude range
mag_range = np.arange(-2.0, 7.0, 1.0)

# Fill the lookup table with the magnitudes
mag_lookup_df.loc[:, 'magnitude'] = mag_range

# Convert the magnitudes to irradiance
mag_lookup_df.loc[:, 'irradiance [W/m^2]'] = \
    mag_lookup_df['magnitude'].apply(lambda x: mag2irr(x))

# Convert the magnitudes to irradiance considering the atmospheric attenuation
mag_lookup_df.loc[:, 'irradiance attn [W/m^2]'] = \
    mag_lookup_df['magnitude'].apply(lambda x: mag2irr(x, use_attn=True))

# Print the resulting lookup table
print(mag_lookup_df)

#%%

# Save the lookup table as an excel sheet
mag_lookup_df.to_excel('magnitude_lookup_table.xlsx')
