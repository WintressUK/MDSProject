import matplotlib
matplotlib.use('TkAgg')  # Use Agg backend for non-GUI operations
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mplticker
from matplotlib.ticker import MultipleLocator
from netCDF4 import Dataset
import pandas as pd
from matplotlib import colormaps
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox
import os
import platform
import sys

#TO DO:
#add option for selecting a range of timesteps and then producing a little animation
#improve gui?

variable_only_data = None
selectedColours = None
variable_data = None
ncx = None
sfc_size = None
selected_variable = None
selected_timestep = None

negis_lats = pd.read_csv("latbook.csv", header = None)
negis_lons = pd.read_csv("lonbook.csv", header = None)

def print_pink(text): #define function for printing output text in pink
    pink_colour_code = '\033[95m' 
    reset_colour_code = '\033[0m'
    print(f"{pink_colour_code}{text}{reset_colour_code}")
    
#define how to open images on each OS
def open_image(file_path):
    if platform.system() == "Windows":
        os.startfile(file_path)
    elif platform.system() == "Darwin":  # macOS
        os.system(f'open "{file_path}"')
    elif platform.system() == "Linux":
        os.system(f'xdg-open "{file_path}"')
    else:
        raise RuntimeError("Unsupported operating system")

#THIS IS THE COMMAND FOR THE LOAD FILE BUTTON
def load_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("NetCDF Files", "*.nc")]
    )
    if file_path:
        print_pink(f"Selected file: {file_path}")
        try:
            global ncx
            ncx = xr.open_dataset(file_path)
            #then get the variables from the selected file
            update_variable_dropdown()
            print_pink(f'File loaded successfully.')
        except Exception as e:
            print_pink(f'Error loading file.')
         
#add a dropdown menu to select variables, based upon the file loaded
def update_variable_dropdown():
    if ncx:
        #exclude variables 'x', 'y', and 'sfc' as these will not be relevant for plotting
        variables = [var for var in ncx.variables if var not in ['x', 'y', 'sfc']]
        variable_dropdown['values'] = variables
        if variables:
            variable_dropdown.current(0)  #select the first variable by default
            
def on_variable_select(event):
    global selected_variable, sfc_size, variable_data
    selected_variable = variable_dropdown.get()
    variable_data = ncx[selected_variable] #filters the nc file to only that variable upon variable selection
    if 'sfc' in variable_data.dims: #looks for the timestep dimension
        sfc_size = variable_data.sizes['sfc']
        update_timestep_slider()
        print_pink(f"Selected variable: {selected_variable}")
    else:
        sfc_size = None
        timestep_slider.config(from_=0, to=0, label='No sfc dimension')
        messagebox.showinfo("Info", "Selected variable does not have 'sfc' dimension.")

def update_timestep_slider():
    if sfc_size is not None:
        timestep_slider.config(from_=0, to=sfc_size-1)
        timestep_slider.set(1)  #optionally set default value
        timestep_slider_label.config(text=f"Select Timestep (1 - {sfc_size-1})")
        
def on_timestep_change(event):
    global selected_timestep
    selected_timestep = timestep_slider.get()
    print_pink(f"Selected timestep: {selected_timestep}")

#SELECT DESIRED COLOURMAP
def update_colourmap(event):
    global selectedColours
    selectedColours = colourmap_dropdown.get()
    print_pink(f"Selected colourmap: {selectedColours}")

#button to confirm selections (mainly exists for debugging)
def confirm_selection():
    if selected_variable is not None and selected_timestep is not None and selectedColours is not None:
        messagebox.showinfo("Selection Confirmed", 
            f"Selected Variable: {selected_variable}\n"
            f"Selected Timestep: {selected_timestep}\n"
            f"Selected Colourmap: {selectedColours}")
    else:
        messagebox.showwarning("Warning", "Please make sure all selections are made.")


def generate_plot():
    global selected_variable, selected_timestep, selectedColours
    if selected_variable and selected_timestep is not None and selectedColours:
        variable_data = ncx[selected_variable]
        processed_data = variable_data.isel(sfc=selected_timestep)
        
        lat_count = variable_data.sizes['y']
        lon_count = variable_data.sizes['x']
        minLat = negis_lats.min().min()
        maxLat = negis_lats.max().max()
        minLon = negis_lons.min().min()
        maxLon = negis_lons.max().max()

        latScale = np.linspace(minLat, maxLat, lat_count)
        lonScale = np.linspace(minLon, maxLon, lon_count)
        
        fig, ax = plt.subplots(dpi=200, figsize=(10, 10))
        map = ax.contourf(lonScale, latScale, processed_data.values, cmap=plt.get_cmap(selectedColours))
        cbar = plt.colorbar(map, ax=ax, label=f'{selected_variable.capitalize()}')

        #axis increments and labels
        ax.xaxis.set_major_locator(MultipleLocator(2))
        ax.yaxis.set_major_locator(MultipleLocator(1))
        ax.set_xlabel('Longitude')
        ax.tick_params(axis='x', labelsize=7)
        ax.set_ylabel('Latitude')
        ax.set_title(f'Plot of variable \'{selected_variable.capitalize()}\' for timestep index: {selected_timestep}')

        #latitude gridlines and greenwich meridian
        ax.yaxis.grid(True, linestyle='--', alpha=0.7)
        ax.axvline(x=0, color='red', linestyle='--', linewidth=0.5)
        
        plt.savefig('graph.png')
        open_image('graph.png')
    
    else:
        messagebox.showwarning("Warning", "Please ensure that the variable, timestep, and colourmap are selected.")
        
def on_close():
    root.destroy()  # Ensure proper cleanup when closing the window
    sys.exit()  # Exit the script
    
def main():
    global root, variable_dropdown, timestep_slider, timestep_slider_label, colourmap_dropdown
    global negis_lats, negis_lons, ncx  # Ensure these are global for use within functions

    try:
        negis_lats = pd.read_csv("latbook.csv", header=None)
        negis_lons = pd.read_csv("lonbook.csv", header=None)

        root = tk.Tk()
        root.title("Plotting Tool")
        root.geometry("800x600")  # Set initial window size
        root.resizable(True, True)  # Allow resizing

        load_button = tk.Button(root, text="Load File", command=load_file)
        load_button.pack(pady=20)

        variable_dropdown_label = tk.Label(root, text="Select Variable")
        variable_dropdown_label.pack(pady=5)

        variable_dropdown = Combobox(root, state="readonly")
        variable_dropdown.pack(pady=5)
        variable_dropdown.bind("<<ComboboxSelected>>", on_variable_select)

        timestep_slider_label = tk.Label(root, text="Select Timestep")
        timestep_slider_label.pack(pady=5)

        timestep_slider = tk.Scale(root, from_=0, to=0, orient="horizontal", length=400)
        timestep_slider.pack(pady=5)
        timestep_slider.bind("<ButtonRelease-1>", on_timestep_change)

        colourmap_label = tk.Label(root, text="Select Colourmap")
        colourmap_label.pack(pady=5)

        colourmap_dropdown = Combobox(root, state="readonly", values=list(colormaps))
        colourmap_dropdown.pack(pady=5)
        colourmap_dropdown.bind("<<ComboboxSelected>>", update_colourmap)

        confirm_button = tk.Button(root, text="Confirm Selections", command=confirm_selection)
        confirm_button.pack(pady=10)

        generate_plot_button = tk.Button(root, text="Generate Plot", command=generate_plot)
        generate_plot_button.pack(pady=10)

        root.protocol("WM_DELETE_WINDOW", on_close)  # Handle window close

        root.mainloop()

    except Exception as e:
        print(f"An error occurred: {e}")
        
if __name__ == "__main__":
    main()
