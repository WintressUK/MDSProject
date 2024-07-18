import easygui
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mplticker
from matplotlib.ticker import MultipleLocator
from netCDF4 import Dataset
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output
from matplotlib import colormaps
import time

#hurting her someone like her

ncx = None
variable_only_data = None
selectedColours = None

negis_lats = pd.read_csv("latbook.csv", header = None)
negis_lons = pd.read_csv("lonbook.csv", header = None)

def print_pink(text): #define function for printing output text in pink
    pink_colour_code = '\033[95m' 
    reset_colour_code = '\033[0m'
    print(f"{pink_colour_code}{text}{reset_colour_code}")

#GET FILE PATH FUNCTION

def get_file_path():
    #file selector gui
    file_path = easygui.fileopenbox(msg="Select a NetCDF File", title="File Selector", filetypes=["*.nc"])
    return file_path

#LOAD FILE FROM SPECIFIED FILE PATH

def load_file(file_path):
    if file_path:
        try:
            global ncx
            ncx = xr.open_dataset(file_path) #open specified file path as xarray object
            print_pink(f'File {file_path} loaded.') #confirm file loading
            #print(ncx.dims)
        except Exception as e:
            print_pink(f'Error loading file {file_path}. Invalid file type.')
    else:
        print('No file path selected.')
        
#IDENTIFY VARIABLES IN FILE AND PROMPT FOR SELECTION

def select_variable(file):
    variable_list = list(ncx.variables)
    selected_variable = easygui.choicebox("Select a Variable", "Variable Selection", variable_list)
    return selected_variable

#SELECT TIMESTEP VALUE

def select_sfc_value(file): #could require a file input and detect sfc size
    sfc_value = easygui.integerbox(msg=f"Enter Timestep (1-{sfc_size-1})", #need to not hard code this?
                                   title="Timestep Selection",
                                   lowerbound=1, upperbound=(sfc_size-1))
    return sfc_value

#SELECT DESIRED COLOURMAP
def select_colormap():
    colourmaps = list(colormaps)
    selected_colourmap = easygui.choicebox("Select Colourmap", "Colourmap Selection", colourmaps)
    return selected_colourmap

#GENERATE PLOT
def generate_plot(lonScale, latScale, processed_data, selectedColours):
    fig, ax = plt.subplots(dpi=200, figsize=(10, 10))
    map = ax.contourf(lonScale, latScale, processed_data.values, cmap=plt.get_cmap(selectedColours))
    cbar = plt.colorbar(map, ax=ax, label=f'{selectedVariable.capitalize()}')

    #configure axis increments and
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.set_xlabel('Longitude')
    ax.tick_params(axis='x', labelsize = 7)
    ax.set_ylabel('Latitude')
    ax.set_title(f'Plot of variable \'{selectedVariable.capitalize()}\' for timestep index: {sfcValue}')

    #confingure latitude gridlines and greenwich meridian
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.axvline(x=0, color='red', linestyle='--', linewidth=0.5)
    
    print_pink("Generated plot.")
    plt.savefig('graph.png')
    
    easygui.msgbox("Generated Plot", image='graph.png')
    

def main():
    #function that obtains file path from user
    file_path = get_file_path()

    #load the file if valid path
    load_file(file_path)
    
    #select a variable from the netcdf file
    if ncx:
        global selectedVariable
        selectedVariable = select_variable(ncx)
        
        if selectedVariable:
            print_pink(f"Selected variable: {selectedVariable}")
            global variable_only_data
            variable_only_data = ncx[selectedVariable]
            
            global lon_count, lat_count, sfc_size
            lon_count = variable_only_data.sizes['x']
            lat_count = variable_only_data.sizes['y']
            sfc_size = variable_only_data.sizes['sfc']
            
            minLat = negis_lats.min().min()
            maxLat = negis_lats.max().max()

            minLon = negis_lons.min().min()
            maxLon = negis_lons.max().max()

            latScale = np.linspace(minLat, maxLat, lat_count)
            lonScale = np.linspace(minLon, maxLon, lon_count)
            
            global sfcValue
            sfcValue = select_sfc_value(ncx)
            
            if sfcValue:
                print_pink(f"Selected timestep: {sfcValue}")
                
                selectedColours = select_colormap()
                
                if selectedColours: 
                    print_pink(f"Selected colourmap: {selectedColours}")
                    
                    #confirm parameters and process data
                    print_pink(f"Selected paramaters: Variable: {selectedVariable}, Timestep: {sfcValue}, Colourmap: {selectedColours}")
                    variable_only_data = ncx[selectedVariable]
                    processed_data = variable_only_data.isel(sfc=sfcValue)
                    
                    #generate plot
                    generate_plot(lonScale, latScale, processed_data, selectedColours)
                    
                else:
                    print_pink("No colourmap selected.")    
                
            else:
                print_pink("No timestep selected.")
            
        else:
            print_pink("No variable selected.")
            
    else:
        print_pink("Stopping program.")
            

if __name__ == "__main__":
    main()
