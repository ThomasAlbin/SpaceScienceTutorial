"""
general/vec.py

This Python file contains miscellaneous, generic functions for vector
computations like the computation of a norm, the dot product or the enclosed
angle between 2 vectors.
"""

# Import standard libraries
import math

def vec_norm(vector, norm='p2'):
    """
    Compute the norm of an n-dimensional vector.

    Parameters
    ----------
    vector : list
        Single n-dimensional vector as a Python list.
    norm : str, optional
        Requested norm type. The default is 'p2'.
        - pX: P Norm. X represents any number larger than 0. E.g., p2 is the
              Euclidean Norm

    Returns
    -------
    norm_res : float
        The resulting norm.

    """

    # if-elif statement for the requested norm
    if 'p' in norm:

        # The second entry of the input string is the p norm value (only valid
        # up to 9)
        p_value = float(norm[1])

        # Compute the norm
        norm_res = math.sqrt(sum(abs(elem)**p_value for elem in vector))

    return norm_res

def vec_dotprod(vector1, vector2):
    """
    Dot product of 2 vectors

    Parameters
    ----------
    vector1 : list
        Input vector 1.
    vector2 : list
        Input vector 2.

    Returns
    -------
    dotp_res : float
        Resulting dot product.

    """
    dotp_res = sum(v1_i * v2_i for v1_i, v2_i in zip(vector1, vector2))

    return dotp_res

def vec_angle(vector1, vector2):

    angle_rad = math.acos(vec_dotprod(vector1, vector2) \
                          / (vec_norm(vector1) * vec_norm(vector2)))

    return angle_rad