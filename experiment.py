import matplotlib
matplotlib.use('TkAgg')  #prevents matplot from interfering with image generation and display
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mplticker
from matplotlib.ticker import MultipleLocator
import pandas as pd
from matplotlib import colormaps
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox
import os
import platform
import sys
import glob
from PIL import Image

variable_only_data = None
selectedColours = None
variable_data = None
ncx = None
sfc_size = None
selected_variable = None
selected_timestep = None
thickness_data = None

root = tk.Tk()
root.title("Plotting Tool")
root.resizable(True, True)
        
timestep_mode = tk.IntVar(value=1)
single_timestep_entry = tk.Entry(root)
start_timestep_entry = tk.Entry(root)
end_timestep_entry = tk.Entry(root)

apply_mask = tk.BooleanVar()

negis_lats = pd.read_csv("latbook.csv", header = None)
negis_lons = pd.read_csv("lonbook.csv", header = None)

latitude_found = False
longitude_found = False
step = 0

selected_lat_variable = None
selected_lon_variable = None
lat_data = None
lon_data = None

def print_pink(text): #define function for printing output text in pink
    pink_colour_code = '\033[95m' 
    reset_colour_code = '\033[0m'
    print(f"{pink_colour_code}{text}{reset_colour_code}")
    
#define how to open images on each OS
def open_image(file_path):
    if platform.system() == "Windows":
        os.startfile(file_path)
    elif platform.system() == "Darwin":  #macOS
        os.system(f'open "{file_path}"')
    elif platform.system() == "Linux":
        os.system(f'xdg-open "{file_path}"')
    else:
        raise RuntimeError("Unsupported operating system")

#THIS IS THE COMMAND FOR THE LOAD FILE BUTTON
def load_file():
    global thickness_data, file_path
    file_path = filedialog.askopenfilename(
        filetypes=[("NetCDF Files", "*.nc")]
    )
    if file_path:
        print_pink(f"Selected file: {file_path}")
        try:
            global ncx
            ncx = xr.open_dataset(file_path)
            thickness_data = ncx['thickness']
            #then get the variables from the selected file
            update_variable_dropdown()
            print_pink(f'File loaded successfully.')
            update_loaded_file()
        except Exception as e:
            print_pink(f'An error occured: {e}')
            
#initialises the popup box for the flowchart of latitude/longitude selection
def initalise_latitude_popup():
    global step
    step = 0 #reset the step whenever the latitude window opens
    latitude_button.config(state=tk.DISABLED)
    auto_latitude_detect() #initalise the process
    
def clear_window(window):
    for widget in window.winfo_children():
        widget.destroy()
        
def on_top_window_close():
    latitude_button.config(state=tk.NORMAL)
    top.destroy()
    
def next():
    global step, latitude_found, longitude_found
    step += 1
    clear_window(top)
    
    if latitude_found and longitude_found:
        print_pink("Latitude and Longitude found.")
        top.destroy()
        latitude_button.config(state=tk.NORMAL)
        selected_latitude_label.config(text="Lat/Lon Uploaded.", fg="#32CD32")
        print_pink(lat_data)
        print_pink(lon_data)
    elif step == 1:
        manual_variable_select()
    elif step == 2: 
        upload_lat_lon_file()
    elif step == 3:
        manual_scale_entry()
    else:
        top.destroy()
        latitude_button.config(state=tk.NORMAL)
          
#popup box executing auto detection of lat/lon in file
def auto_latitude_detect():
    global top, latitude_found, longitude_found
    top = tk.Toplevel(root)
    #top.geometry("750x250")
    top.title("Scale Selection")
    top.protocol("WM_DELETE_WINDOW", on_top_window_close)
    
    if ncx is not None:
        global lat_data, lon_data
        
        auto_latitude_detect_label = tk.Label(top, text= "Auto Scale Detection")
        auto_latitude_detect_label.pack(pady=5)
    
        for var in ncx.variables:
            if var in ['lat', 'lats']:
                lat_data = ncx[var]
                latitude_variable_name = var
                latitude_found = True
                break
            
        if lat_data == None:
            no_latitude_label = tk.Label(top, text = "No Latitudes Autodetected.")
            no_latitude_label.pack(pady =5)
        elif lat_data is not None:
            latitude_label = tk.Label(top, text=f"Latitudes Detected from Variable {latitude_variable_name}")
            latitude_label.pack(pady=5)
            
        for var in ncx.variables:
            if var in ['lon', 'lons']:
                lon_data = ncx[var]
                longitude_variable_name = var
                longitude_found = True
                break
                
        if lon_data == None:
            no_longitude_label = tk.Label(top, text = "No Longitudes Autodetected.")
            no_longitude_label.pack(pady =5)
        elif lon_data is not None:
            longitude_label = tk.Label(top, text=f"Longitudes Detected from Variable {longitude_variable_name}")
            longitude_label.pack(pady=5)
            
        auto_next_button = tk.Button(top, text="Next", command=next)
        auto_next_button.pack(pady=5)
    
    else:
        nothing_selected_label = tk.Label(top, text= "Please load a file.")
        nothing_selected_label.pack(pady=5)
        
def manual_variable_select(): #STEP 1
    global manual_variable_select_combobox, manual_variable_select_combobox_lon, latitude_found, longitude_found, lat_data, lon_data
    
    manual_variable_select_top_label = tk.Label(top, text = "Manual Select Lat and Lon Variable")
    manual_variable_select_top_label.pack(pady=5)
    
    lat_frame = tk.Frame(top)
    lon_frame = tk.Frame(top)
    
    lat_frame.pack(pady=5)
    lon_frame.pack(pady=5)
    
    manual_variable_select_combobox_label = tk.Label(lat_frame, text = "Select Latitude Variable")
    manual_variable_select_combobox_label.pack(side=tk.LEFT, padx=5, pady=10)
    
    manual_variable_select_combobox = Combobox(lat_frame, state="readonly", values = list(ncx.variables))
    manual_variable_select_combobox.pack(pady=10)
    manual_variable_select_combobox.bind("<<ComboboxSelected>>", on_lat_variable_select)
    
    manual_variable_select_combobox_label_lon = tk.Label(lon_frame, text = "Select Longitude Variable")
    manual_variable_select_combobox_label_lon.pack(side=tk.LEFT, padx=5, pady=10)
    
    manual_variable_select_combobox_lon = Combobox(lon_frame, state="readonly", values = list(ncx.variables))
    manual_variable_select_combobox_lon.pack(pady=10)
    manual_variable_select_combobox_lon.bind("<<ComboboxSelected>>", on_lon_variable_select)
    
    if selected_lon_variable:
        longitude_found = True
        lon_data = ncx[selected_lon_variable]
    if selected_lat_variable:
        latitude_found = True
        lat_data = ncx[selected_lat_variable]
        
    manual_variable_select_next = tk.Button(top, text="Next", command=next)
    manual_variable_select_next.pack(pady=5)
    
def upload_lat_lon_file(): #STEP 2
    global latitude_found, longitude_found, loaded_lat_label, loaded_lon_label
    upload_lat_lon_file_top_label = tk.Label(top, text = "Upload Lat/Lon File")
    upload_lat_lon_file_top_label.pack(pady=5)
    
    lat_frame = tk.Frame(top)
    lon_frame = tk.Frame(top)
    
    lat_frame.pack(pady=5)
    
    lat_label = tk.Label(lat_frame, text = "Select Latitude File")
    lat_label.pack(side=tk.LEFT, padx=5, pady=10)
    
    lat_file_button = tk.Button(lat_frame, text="Upload File", command=load_lat_file)
    lat_file_button.pack(pady=5)
    
    loaded_lat_label = tk.Label(top, text = "Latitude File: None")
    loaded_lat_label.pack(pady=5)
    
    lon_frame.pack(pady=5)
    
    lon_label = tk.Label(lon_frame, text = "Select Longitude File")
    lon_label.pack(side=tk.LEFT, padx=5, pady=10)
    
    lon_file_button = tk.Button(lon_frame, text="Upload File", command=load_lon_file)
    lon_file_button.pack(pady=5)
    
    loaded_lon_label = tk.Label(top, text = "Longitude File: None")
    loaded_lon_label.pack(pady=5)
        
    #next button
    next_button = tk.Button(top, text="Next", command=next)
    next_button.pack(pady=5)
      
def load_lat_file():
    global lat_data, latitude_found
    lat_file_path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")]
    )
    lat_data = pd.read_csv(lat_file_path)
    latitude_found = True
    
    if lat_data is not None:
        loaded_lat_label.config(text=f"Latitude File: {lat_file_path}", fg="#32CD32")
    
def load_lon_file():
    global lon_data, longitude_found
    lon_file_path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")]
    )
    lon_data = pd.read_csv(lon_file_path)
    longitude_found = True
    
    if lon_data is not None:
        loaded_lon_label.config(text=f"Latitude File: {lon_file_path}", fg="#32CD32")
        
def manual_scale_entry(): #STEP 3
    global min_lat_entry, max_lat_entry, min_lon_entry, max_lon_entry
    lat_frame = tk.Frame(top)
    lat_frame.pack(pady=5)
    
    min_lat_label = tk.Label(lat_frame, text="Min Lat")
    min_lat_label.pack(side=tk.LEFT, padx=5)
        
    min_lat_entry = tk.Entry(lat_frame)
    min_lat_entry.pack(side=tk.LEFT, padx=5)
    
    max_lat_label = tk.Label(lat_frame, text="Max Lat")
    max_lat_label.pack(side=tk.LEFT, padx=5)
        
    max_lat_entry = tk.Entry(lat_frame)
    max_lat_entry.pack(side=tk.LEFT, padx=5)
    
    lon_frame = tk.Frame(top)
    lon_frame.pack(pady=5)
    
    min_lon_label = tk.Label(lon_frame, text="Min Lon")
    min_lon_label.pack(side=tk.LEFT, padx=5)
        
    min_lon_entry = tk.Entry(lon_frame)
    min_lon_entry.pack(side=tk.LEFT, padx=5)
    
    max_lon_label = tk.Label(lon_frame, text="Max Lon")
    max_lon_label.pack(side=tk.LEFT, padx=5)
        
    max_lon_entry = tk.Entry(lon_frame)
    max_lon_entry.pack(side=tk.LEFT, padx=5)
    
    #next button (presented as quit button)
    buttons_frame = tk.Frame(top)
    buttons_frame.pack(pady=5)
    
    confirm_button = tk.Button(top, text="Confirm", command=confirm_manual_scale)
    confirm_button.pack(side=tk.LEFT, padx=5)
    
    next_button = tk.Button(top, text="Quit", command=next)
    next_button.pack(side=tk.LEFT, padx=5)
    
def confirm_manual_scale():
    global min_lat, max_lat, min_lon, max_lon
    global latitude_found, longitude_found
    global lat_data, lon_data
    
    min_lat = int(min_lat_entry.get())
    max_lat = int(max_lat_entry.get())
    min_lon = int(min_lon_entry.get())
    max_lon = int(max_lon_entry.get())
    
    latitude_found = True
    longitude_found = True
    
    lat_data = [min_lat, max_lat]
    lon_data = [min_lon, max_lon]
    
    next() #call next function to check latitude_found and longitude_found again
    
#add a dropdown menu to select variables, based upon the file loaded
def update_variable_dropdown():
    if ncx:
        #exclude variables 'x', 'y', and 'sfc' as these will not be relevant for plotting
        variables = [var for var in ncx.variables if var not in ['x', 'y', 'sfc', 'crs']]
        variable_dropdown['values'] = variables
        mask_variable_dropdown['values'] = variables

#assigns selected variable to an object, and sections the data based on selected variable
#collects timestep number from selected variable 
def on_variable_select(event):
    global selected_variable, sfc_size, variable_data
    selected_variable = variable_dropdown.get()
    variable_data = ncx[selected_variable] #filters the nc file to only that variable upon variable selection
    if 'sfc' in variable_data.dims: #looks for the timestep dimension
        sfc_size = variable_data.sizes['sfc']
        update_timestep_range()
        print_pink(f"Selected variable: {selected_variable}")
    else:
        sfc_size = None
        messagebox.showinfo("Info", "Selected variable does not have 'sfc' dimension.")
   
#assigns selected mask variable to an object to be used in generate_plot function     
def on_mask_variable_select(event):
    global selected_mask_variable
    selected_mask_variable = mask_variable_dropdown.get()
    
def on_lat_variable_select(event):
    global selected_lat_variable
    selected_lat_variable = manual_variable_select_combobox.get()
    
def on_lon_variable_select(event):
    global selected_lon_variable
    selected_lon_variable = manual_variable_select_combobox_lon.get()

#enables and disabled the timestep options based on whether single timestep or range is selected        
def toggle_timestep_mode():
    mode = timestep_mode.get()
    if mode == 1:
        single_timestep_entry.config(state=tk.NORMAL)
        start_timestep_entry.config(state=tk.DISABLED)
        end_timestep_entry.config(state=tk.DISABLED)
    elif mode == 2:
        single_timestep_entry.config(state=tk.DISABLED)
        start_timestep_entry.config(state=tk.NORMAL)
        end_timestep_entry.config(state=tk.NORMAL)
        
#shows and hides masking options based on whether apply mask box is checked
def toggle_masking_mode():
    if apply_mask.get():
        mask_variable_dropdown.config(state=tk.NORMAL)
        masking_range_start_entry.config(state=tk.NORMAL)
        masking_range_end_entry.config(state=tk.NORMAL)
    else:
        mask_variable_dropdown.config(state=tk.DISABLED)
        masking_range_start_entry.config(state=tk.DISABLED)
        masking_range_end_entry.config(state=tk.DISABLED)

#changes the label that shows the current timestep range 
def update_timestep_range():
    if sfc_size is not None:
        timestep_range_label_text.config(text=f"Timestep Range: 0 to {sfc_size-1}")

#changes the label that shows the current loaded file       
def update_loaded_file():
    if ncx is not None:
        loaded_file_label.config(text=f"Loaded File: {file_path}", fg="#32CD32")

#assigns selected colourmap to an object
def update_colourmap(event):
    global selectedColours
    selectedColours = colourmap_dropdown.get()
    print_pink(f"Selected colourmap: {selectedColours}")
 
#mostly a debugging button that shows all current selections from all the buttons       
def confirm_selection():
    if selected_variable is not None and selectedColours is not None:
        if timestep_mode.get() == 1 and apply_mask.get():
            selected_timestep = single_timestep_entry.get()
            messagebox.showinfo("Selection Confirmed", 
                f"Selected Variable: {selected_variable}\n"
                f"Selected Timestep: {selected_timestep}\n"
                f"Apply Mask: {apply_mask.get()}\n"
                f"Mask Variable: {selected_mask_variable}\n"
                f"Mask Threshold Start: {masking_range_start_entry.get()}\n"
                f"Mask Threshold End: {masking_range_end_entry.get()}\n"
                f"Selected Colourmap: {selectedColours}")
        elif timestep_mode.get() == 2 and apply_mask.get():
            start_timestep = start_timestep_entry.get()
            end_timestep = end_timestep_entry.get()
            messagebox.showinfo("Selection Confirmed", 
                f"Selected Variable: {selected_variable}\n"
                f"Start Timestep: {start_timestep}\n"
                f"End Timestep: {end_timestep}\n"
                f"Apply Mask: {apply_mask.get()}\n"
                f"Mask Variable: {selected_mask_variable}\n"
                f"Mask Threshold Start: {masking_range_start_entry.get()}\n"
                f"Mask Threshold End: {masking_range_end_entry.get()}\n"
                f"Selected Colourmap: {selectedColours}")
        elif timestep_mode.get() == 1 and not apply_mask.get():
            selected_timestep = single_timestep_entry.get()
            messagebox.showinfo("Selection Confirmed", 
                f"Selected Variable: {selected_variable}\n"
                f"Selected Timestep: {selected_timestep}\n"
                f"Apply Mask: {apply_mask.get()}\n"
                f"Selected Colourmap: {selectedColours}")
        elif timestep_mode.get() == 2 and not apply_mask.get():
            start_timestep = start_timestep_entry.get()
            end_timestep = end_timestep_entry.get()
            messagebox.showinfo("Selection Confirmed", 
                f"Selected Variable: {selected_variable}\n"
                f"Start Timestep: {start_timestep}\n"
                f"End Timestep: {end_timestep}\n"
                f"Apply Mask: {apply_mask.get()}\n"
                f"Selected Colourmap: {selectedColours}")
    else:
        messagebox.showwarning("Warning", "Please make sure all selections are made.")
        
#procedure for collating multiple plots into an animation using pillow library       
def create_gif():
    print_pink("Creating GIF...")
    #retrieve all image filenames in the 'plots' directory
    filenames = glob.glob("plots/plot_*.png")
    
    # Sort filenames numerically (assuming consistent naming)
    filenames.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))

    # Open images and create GIF
    images = [Image.open(filename) for filename in filenames]
    
    if images:
        gif_filename = "animation.gif"
        images[0].save(gif_filename, save_all=True, append_images=images[1:], duration=100, loop=0)
        open_image(gif_filename)
        for filename in filenames:
            os.remove(filename)
    else:
        messagebox.showerror("Error", "No images found to create GIF.")

#generates plot based on timestep and masking options
def generate_plot():
    global selected_variable, selectedColours
    
    minLat = negis_lats.min().min()
    maxLat = negis_lats.max().max()
    minLon = negis_lons.min().min()
    maxLon = negis_lons.max().max()

    if not apply_mask.get():
        if timestep_mode.get() == 1:
            if selected_variable and single_timestep_entry.get() is not None and selectedColours:
                variable_data = ncx[selected_variable]
                processed_data = variable_data.isel(sfc=int(single_timestep_entry.get()))
                
                lat_count = variable_data.sizes['y']
                lon_count = variable_data.sizes['x']
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
                ax.set_title(f'Plot of variable \'{selected_variable.capitalize()}\' for timestep index: {single_timestep_entry.get()}')

                #latitude gridlines and greenwich meridian
                ax.yaxis.grid(True, linestyle='--', alpha=0.7)
                ax.axvline(x=0, color='red', linestyle='--', linewidth=0.5)
                
                plt.savefig('graph.png')
                open_image('graph.png')
        
            else:
                messagebox.showwarning("Warning", "Please ensure that the variable, timestep, and colourmap are selected.")
        else:
            
            if selected_variable and start_timestep_entry.get() and end_timestep_entry.get() is not None and selectedColours:
                
                start_timestep = int(start_timestep_entry.get())
                end_timestep = int(end_timestep_entry.get())
                
                for x in range(start_timestep, (end_timestep+1)):
                    variable_data = ncx[selected_variable]
                    processed_data = variable_data.isel(sfc=x)
                    
                    lat_count = variable_data.sizes['y']
                    lon_count = variable_data.sizes['x']
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
                    ax.set_title(f'Plot of variable \'{selected_variable.capitalize()}\' for timestep index: {x}')

                    #latitude gridlines and greenwich meridian
                    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
                    ax.axvline(x=0, color='red', linestyle='--', linewidth=0.5)
                    
                    #save each plot with filename corresponding to x
                    filename = f"plots/plot_{x}.png"
                    print_pink(f"Generated plot {x}")
                    plt.savefig(filename)
                    plt.close(fig) 
                    
                create_gif()
                
            else: 
                messagebox.showwarning("Warning", "Please ensure that the variable, start and end timesteps, and colourmap are selected.")
                
    if apply_mask.get():
        
        if timestep_mode.get() == 1:
            
            if selected_variable and single_timestep_entry.get() is not None and selectedColours:
                
                #select current timestep in the whole dataset
                current_timestep_data = ncx.isel(sfc=int(single_timestep_entry.get()))
                
                #select current timestep for only MASKING VARIABLE
                masking_variable_data = current_timestep_data[selected_mask_variable] #selected_mask_variable assigned in above function on_mask_variable_select
                masking_threshold_start = masking_range_start_entry.get() #retrieves threshold start from entry box
                masking_threshold_end = masking_range_end_entry.get() #retrieves threshold end from entry box
                mask1 = masking_variable_data < int(masking_threshold_start)
                mask2 = masking_variable_data > int(masking_threshold_end)
                combined_mask = mask1 | mask2
                
                #apply the mask (created above) to relevant variable in the current timestep dataset
                variable_data = current_timestep_data[selected_variable]
                masked_data = variable_data.where(combined_mask, drop = True)
                
                lat_count = masked_data.sizes['y']
                lon_count = masked_data.sizes['x']
                latScale = np.linspace(minLat, maxLat, lat_count)
                lonScale = np.linspace(minLon, maxLon, lon_count)
                
                fig, ax = plt.subplots(dpi=200, figsize=(10, 10))
                map = ax.contourf(lonScale, latScale, masked_data.values, cmap=plt.get_cmap(selectedColours))
                cbar = plt.colorbar(map, ax=ax, label=f'{selected_variable.capitalize()}')

                #axis increments and labels
                ax.xaxis.set_major_locator(MultipleLocator(2))
                ax.yaxis.set_major_locator(MultipleLocator(1))
                ax.set_xlabel('Longitude')
                ax.tick_params(axis='x', labelsize=7)
                ax.set_ylabel('Latitude')
                ax.set_title(f'Plot of variable \'{selected_variable.capitalize()}\' for timestep index: {single_timestep_entry.get()}')

                #latitude gridlines and greenwich meridian
                ax.yaxis.grid(True, linestyle='--', alpha=0.7)
                ax.axvline(x=0, color='red', linestyle='--', linewidth=0.5)
                
                plt.savefig('graph.png')
                open_image('graph.png')
                
            else:
                messagebox.showwarning("Warning", "Please ensure that the variable, timestep, and colourmap are selected.")
                
        if timestep_mode.get() == 2:
            
            if selected_variable and single_timestep_entry.get() is not None and selectedColours:
                
                start_timestep = int(start_timestep_entry.get())
                end_timestep = int(end_timestep_entry.get())
                
                for x in range(start_timestep, (end_timestep+1)):
                    current_timestep_data = ncx.isel(sfc=x)
                    
                    masking_variable_data = current_timestep_data[selected_mask_variable] #selected_mask_variable assigned in above function on_mask_variable_select
                    masking_threshold_start = masking_range_start_entry.get() #retrieves threshold start from entry box
                    masking_threshold_end = masking_range_end_entry.get() #retrieves threshold end from entry box
                    mask1 = masking_variable_data < int(masking_threshold_start)
                    mask2 = masking_variable_data > int(masking_threshold_end)
                    combined_mask = mask1 | mask2
                    
                    #apply the mask (created above) to relevant variable in the current timestep dataset
                    variable_data = current_timestep_data[selected_variable]
                    masked_data = variable_data.where(combined_mask, drop = True)
                    
                    lat_count = masked_data.sizes['y']
                    lon_count = masked_data.sizes['x']
                    latScale = np.linspace(minLat, maxLat, lat_count)
                    lonScale = np.linspace(minLon, maxLon, lon_count)
                
                    fig, ax = plt.subplots(dpi=200, figsize=(10, 10))
                    map = ax.contourf(lonScale, latScale, masked_data.values, cmap=plt.get_cmap(selectedColours))
                    cbar = plt.colorbar(map, ax=ax, label=f'{selected_variable.capitalize()}')

                    #axis increments and labels
                    ax.xaxis.set_major_locator(MultipleLocator(2))
                    ax.yaxis.set_major_locator(MultipleLocator(1))
                    ax.set_xlabel('Longitude')
                    ax.tick_params(axis='x', labelsize=7)
                    ax.set_ylabel('Latitude')
                    ax.set_title(f'Plot of variable \'{selected_variable.capitalize()}\' for timestep index: {x}')

                    #latitude gridlines and greenwich meridian
                    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
                    ax.axvline(x=0, color='red', linestyle='--', linewidth=0.5)
                    
                    #save each plot with filename corresponding to x
                    filename = f"plots/plot_{x}.png"
                    print_pink(f"Generated plot {x}")
                    plt.savefig(filename)
                    plt.close(fig) 
                    
                create_gif()
                    
def on_close():
    root.destroy()  
    sys.exit()  
    
def main():
    global root, variable_dropdown, mask_variable_dropdown, colourmap_dropdown, timestep_range_label_text, timestep_mode, single_timestep_entry, start_timestep_entry, end_timestep_entry
    global negis_lats, negis_lons, ncx, apply_mask, mask_frame, masking_range_start_entry, masking_range_end_entry, loaded_file_label
    global latitude_button, selected_latitude_label

    try:
        negis_lats = pd.read_csv("latbook.csv", header=None)
        negis_lons = pd.read_csv("lonbook.csv", header=None)

        load_button = tk.Button(root, text="Load File", command=load_file)
        load_button.pack(pady=5)
        
        loaded_file_label = tk.Label(root, text="Loaded File: None")
        loaded_file_label.pack(pady=5)
        
        latitude_button = tk.Button(root, text="Load Lat/Lon", command=initalise_latitude_popup)
        latitude_button.pack(pady=5)
        
        selected_latitude_label = tk.Label(root, text="No lat/lon loaded.")
        selected_latitude_label.pack(pady=5)

        variable_dropdown_label = tk.Label(root, text="Select Variable:")
        variable_dropdown_label.pack(pady=5)

        variable_dropdown = Combobox(root, state="readonly")
        variable_dropdown.pack(pady=5)
        variable_dropdown.bind("<<ComboboxSelected>>", on_variable_select)
        
        #label the radio buttons
        timestep_range_label = tk.Label(root, text="Select Single Timestep or Range:")
        timestep_range_label.pack(pady=5)
        
        #add radio buttons in!
        timestep_mode = tk.IntVar(value=1) #define the variable that the radio buttons change
        single_timestep_radio = tk.Radiobutton(root, text = "Single Timestep", variable = timestep_mode, value = 1, command = toggle_timestep_mode)
        single_timestep_radio.pack(pady=5)
        double_timestep_radio = tk.Radiobutton(root, text = "Timestep Range", variable = timestep_mode, value = 2, command = toggle_timestep_mode)
        double_timestep_radio.pack(pady=5)
        
        single_frame = tk.Frame(root)
        single_frame.pack(pady=5)
        
        single_timestep_label = tk.Label(single_frame, text="Enter Single Timestep:")
        single_timestep_label.pack(side=tk.LEFT, padx=5)
        
        single_timestep_entry = tk.Entry(single_frame)
        single_timestep_entry.pack(pady=5)
        
        range_frame = tk.Frame(root)
        range_frame.pack(pady=5)
        
        start_timestep_label = tk.Label(range_frame, text="Start Timestep")
        start_timestep_label.pack(side=tk.LEFT, padx=5)
        
        start_timestep_entry = tk.Entry(range_frame)
        start_timestep_entry.pack(side=tk.LEFT, padx=5)
        
        end_timestep_label = tk.Label(range_frame, text="End Timestep")
        end_timestep_label.pack(side=tk.LEFT, padx=5)
        
        end_timestep_entry = tk.Entry(range_frame)
        end_timestep_entry.pack(side=tk.LEFT, padx=5)
        
        timestep_range_label_text = tk.Label(root, text="Timestep Range: N/A")
        timestep_range_label_text.pack(pady=5)
        
        toggle_timestep_mode()
        
        #add mask applying toggle
        apply_mask_toggle = tk.Checkbutton(root, text = "Apply Mask?", variable = apply_mask, command = toggle_masking_mode)
        apply_mask_toggle.pack(pady=5)
        
        #add frame for masking options
        mask_frame = tk.Frame(root)
        mask_frame.pack(pady=5)
        
        mask_variable_dropdown_label = tk.Label(mask_frame, text="Masking Variable:")
        mask_variable_dropdown_label.pack(side=tk.LEFT, padx=5)
        
        mask_variable_dropdown = Combobox(mask_frame, state="readonly")
        mask_variable_dropdown.pack(side=tk.LEFT, pady=5)
        mask_variable_dropdown.bind("<<ComboboxSelected>>", on_mask_variable_select) #assigns the selected variable to 'selected_mask_variable'

        masking_range_start_label = tk.Label(mask_frame, text="Range Start:")
        masking_range_start_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        masking_range_start_entry = tk.Entry(mask_frame)
        masking_range_start_entry.pack(side=tk.LEFT, pady=5)
        
        masking_range_end_label = tk.Label(mask_frame, text="Range End:")
        masking_range_end_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        masking_range_end_entry = tk.Entry(mask_frame)
        masking_range_end_entry.pack(side=tk.LEFT, pady=5)
        
        toggle_masking_mode()

        colourmap_label = tk.Label(root, text="Select Colourmap")
        colourmap_label.pack(pady=5)

        colourmap_dropdown = Combobox(root, state="readonly", values=list(colormaps))
        colourmap_dropdown.pack(pady=5)
        colourmap_dropdown.bind("<<ComboboxSelected>>", update_colourmap)

        confirm_button = tk.Button(root, text="Confirm Selections", command=confirm_selection)
        confirm_button.pack(pady=10)

        generate_plot_button = tk.Button(root, text="Generate Plot", command=generate_plot)
        generate_plot_button.pack(pady=10)

        root.protocol("WM_DELETE_WINDOW", on_close)  #handle window close

        root.mainloop()

    except Exception as e:
        print(f"An error occurred: {e}")
        
main()