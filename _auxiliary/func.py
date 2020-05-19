# Import the modules
import datetime
import pathlib
import urllib.request
import os


import numpy as np
import spiceypy

#%%

# We define a function that is useful for downloading files. Some files, like
# SPICE kernel files, are large and cannot be uploaded on the GitHub
# repository. Thus, this helper function shall support you for the future
# file and kernel management (if needed).
def download_file(dl_path, dl_url):
    """
    download_file(DL_PATH, DL_URL)

    This helper function supports one to download files from the Internet and
    stores them in a local directory.

    Parameters
    ----------
    DL_PATH : str
        Download path on the local machine, relative to this function.
    DL_URL : str
        Download url of the requested file.
    """

    # Obtain the file name from the url string. The url is split at
    # the "/", thus the very last entry of the resulting list is the file's
    # name
    file_name = dl_url.split('/')[-1]

    # Create necessary sub-directories in the DL_PATH direction (if not
    # existing)
    pathlib.Path(dl_path).mkdir(parents=True, exist_ok=True)

    # If the file is not present in the download directory -> download it
    if not os.path.isfile(dl_path + file_name):

        # Download the file with the urllib  package
        urllib.request.urlretrieve(dl_url, dl_path + file_name)

#%%

