# Import modules
import numpy as np

def phi_func(index, phase_angle):
    """
    Phase function that is needed for the reduced magnitude. The function has
    two versions, depending on the index ('1' or '2').

    Parameters
    ----------
    index : str
        Phase function index / version. '1' or '2'.
    phase_angle : float
        Phase angle of the asteroid in radians.

    Returns
    -------
    phi : float
        Phase function result.

    """

    # Dictionary that contains the A and B constants, depending on the index /
    # version
    a_factor = {'1': 3.33, \
                '2': 1.87}

    b_factor = {'1': 0.63, \
                '2': 1.22}

    # Phase function
    phi = np.exp(-1.0 * a_factor[index] \
                 *+ ((np.tan(0.5 * phase_angle) ** b_factor[index])))

    # Return the phase function result
    return phi

def red_mag(abs_mag, phase_angle, slope_g):
    """
    Reduced magnitude of an asteroid, depending on the absolute magnitude,
    phase angle and slope parameter (G)

    Parameters
    ----------
    abs_mag : float
        Absolute magnitude.
    phase_angle : float
        Phase angle in radians.
    slope_g : float
        Slope parameter (G), between 0 and 1.

    Returns
    -------
    r_mag : float
        Reduced magnitude.

    """

    # Computation of the reduced magnitude
    r_mag = abs_mag - 2.5 * np.log10((1.0 - slope_g) \
                                     * phi_func(index='1', \
                                                phase_angle=phase_angle) \
                                     + slope_g \
                                     * phi_func(index='2', \
                                                phase_angle=phase_angle))

    # Return the reduced magnitude
    return r_mag

def app_mag(abs_mag, phase_angle, slope_g, d_ast_sun, d_ast_earth):
    """
    Apparent / Visual magnitude of an asteroid (not considering atmospheric
    attenuation), depending on the absolute magnitude, phase angle, the slope
    parameter (G) as well as the distance between the asteroid and Earth,
    respectively the Sun

    Parameters
    ----------
    abs_mag : float
        Absolute magnitude.
    phase_angle : float
        Phase angle in radians.
    slope_g : float
        Slope parameter (G).
    d_ast_sun : float
        Distance between the asteroid and the Sun in AU.
    d_ast_earth : float
        Distance between the asteroid and the Earth in AU.

    Returns
    -------
    mag : float
        Apparent / visual magnitude.

    """

    # Compute the apparent / visual magnitude
    mag = red_mag(abs_mag, phase_angle, slope_g) \
          + 5.0 * np.log10(d_ast_sun * d_ast_earth)

    # Return the apparent magnitude
    return mag
