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

# We define a function to add a new column in an already existing database
# table. This code snippet may be helpful in the future
def add_col2tab(con_db, cur_db, tab_name, col_name, col_type):
    """
    This function adds a new column to an already existing SQLite table.
    Setting a new or editing an existing key (primary or foreign) is not
    possible.

    Parameters
    ----------
    con_db : sqlite3.Connection
        Connection object to the SQLite database.
    cur_db : sqlite3.Cursor
        Connection corresponding cursor.
    tab_name : str
        Table name.
    col_name : str
        New column name that shall be added.
    col_type : str
        New column name corresponding SQLite column type.

    Returns
    -------
    None.

    """

    # Iterate through all existing column names of the database table using
    # the PRAGMA table_info command
    for row in cur_db.execute(f'PRAGMA table_info({tab_name})'):

        # If the column exists: exit the function
        if row[1] == col_name:
            break

    # If the column is not existing yet, add the new column
    else:
        cur_db.execute(f'ALTER TABLE {tab_name} ' \
                       f'ADD COLUMN {col_name} {col_type}')
        con_db.commit()