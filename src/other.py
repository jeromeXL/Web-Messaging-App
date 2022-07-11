from src.data_store import *
import os

'''
CLEAR

Resets the internal data of the application to its initial state

Arguments: n/a

Exceptions: n/a

Returns: n/a

'''

def clear_v1():
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    store['dms'] = []
    store['standups'] = []


    store['reset_codes'] = []
    store['notifications'] = []
    current = os.getcwd()
    folder = current + '/src/static'
    for filename in os.listdir(folder):
        if filename != 'default.jpg':
            file_path = os.path.join(folder, filename)
            os.remove(file_path)

    data_store.set(store)

