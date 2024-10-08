import sys
import matplotlib
matplotlib.use('TkAgg')  #prevents matplot from interfering with image generation and display
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mplticker
from matplotlib.ticker import MultipleLocator
import pandas as pd 
from matplotlib import colormaps #allows colours in plotting
import tkinter as tk #import core ui module
from tkinter import filedialog, messagebox #allows showing error messsages and file selection
from tkinter.ttk import Combobox #allows dropdowns
import os #info about system os
import platform #info about system platform
import sys #system operations
import glob #global file search
from PIL import Image #support for image manipulation
import scipy.stats as stats #statistics package
import matplotlib.colors as mcolors #allows access to colourmap names
from ttkbootstrap import Style #adds more modern ui theme
from ttkbootstrap.tooltip import ToolTip #used for tooltip documentation


#create the base window for the UI
root = tk.Tk()
root.title("Plotting Tool")
root.resizable(True, True)

#initialise variables
variable_only_data = None
selectedColours = None
variable_data = None
ncx = None
sfc_size = None
selected_variable = None
selected_timestep = None
thickness_data = None

timestep_mode = tk.IntVar(value=1)
single_timestep_entry = tk.Entry(root)
start_timestep_entry = tk.Entry(root)
end_timestep_entry = tk.Entry(root)
apply_mask = tk.BooleanVar()
apply_topography = tk.BooleanVar()

latitude_found = False
longitude_found = False
step = 0

selected_lat_variable = None
selected_lon_variable = None
lat_data = None
lon_data = None

latitudes = [0, 0]
longitudes = [0, 0]

#define function for printing output text in pink, used for distinctive printing of loading messages in console
def print_pink(text):
    pink_colour_code = '\033[95m' 
    reset_colour_code = '\033[0m'
    print(f"{pink_colour_code}{text}{reset_colour_code}")

#formal def of protocol for closing the ui
def on_close():
    root.destroy()  
    sys.exit()  
    
#define how to open images on each OS for displaying the plotted output
def open_image(file_path):
    if platform.system() == "Windows":
        os.startfile(file_path)
    elif platform.system() == "Darwin":  #macOS
        os.system(f'open "{file_path}"')
    elif platform.system() == "Linux":
        os.system(f'xdg-open "{file_path}"')
    else:
        raise RuntimeError("Unsupported operating system")


##LOAD FILE BUTTON##
#command for the load file button
def load_file():
    global thickness_data, file_path
    file_path = filedialog.askopenfilename(
        filetypes=[("NetCDF Files", "*.nc")] #select file from system
    )
    if file_path:
        print_pink(f"Selected file: {file_path}") #message confirming file selection
        try:
            global ncx
            ncx = xr.open_dataset(file_path) #save selected nc file as xarray object
            print_pink(f"Data Shape: {ncx['thickness'].shape[1]}")
            thickness_data = ncx['thickness']
            #then get the variables from the selected file by calling update_variable_dropdown
            update_variable_dropdown()
            update_loaded_file()
        except Exception as e:
            print_pink(f'An error occured: {e}')
            
#add a dropdown menu to select variables, based upon the file loaded
def update_variable_dropdown():
    if ncx:
        #exclude variables 'x', 'y', and 'sfc' as these will not be relevant for plotting
        variables = [var for var in ncx.variables if var not in ['x', 'y', 'sfc', 'crs']]
        variable_dropdown['values'] = variables
        mask_variable_dropdown['values'] = variables
        topography_variable_dropdown['values'] = variables
    else:
        raise RuntimeError("Unable to import file variables.")
            

##LATITUDE/LONGITUDE UPLOAD BOX##
#initialises the popup box for the flowchart of latitude/longitude selection
def initalise_latitude_popup():
    global step
    step = 0 #reset the step whenever the latitude window opens
    latitude_button.config(state=tk.DISABLED)
    auto_latitude_detect() #initalise the process

#protocol for resetting contents of a ui frame
def clear_window(window):
    for widget in window.winfo_children():
        widget.destroy()

#formalises closing protocol for popup windows
def on_top_window_close():
    latitude_button.config(state=tk.NORMAL)
    top.destroy()

#function applied to the 'next' button in the lat/lon upload menu, cycles through 4 states until lat/lon found using counter
def next():
    global step, latitude_found, longitude_found
    step += 1
    clear_window(top)
    
    if latitude_found and longitude_found:
        print_pink("Latitude and Longitude found.")
        top.destroy()
        selected_latitude_label.config(text="Lat/Lon Uploaded.", fg="#32CD32")
        find_lat_lon_scale()
    elif step == 1:
        manual_variable_select()
    elif step == 2: 
        upload_lat_lon_file()
    elif step == 3:
        manual_scale_entry()
    else:
        top.destroy()
        latitude_button.config(state=tk.NORMAL) #closes down the popup and resets lat/lon upload button if no lat/lon is found by the end of the process
          
#popup box executing auto detection of lat/lon in file
def auto_latitude_detect():
    global top, latitude_found, longitude_found
    top = tk.Toplevel(root)
    top.title("Scale Selection")
    top.protocol("WM_DELETE_WINDOW", on_top_window_close) #sets function for controlled window closure
    
    if ncx is not None:
        global lat_data, lon_data
        
        auto_latitude_detect_label = tk.Label(top, text= "Auto Scale Detection")
        auto_latitude_detect_label.pack(pady=5)
    
        for var in ncx.variables:
            if var in ['lat', 'lats', 'latitude', 'latitudes']: #state common names for lats in files
                lat_data = ncx[var] #if latitude variable found, imports its data to lat_data object for later use
                latitude_variable_name = var
                latitude_found = True
                break
            
        if lat_data == None:
            no_latitude_label = tk.Label(top, text = "No Latitudes Autodetected.") #informs user if nothing is detected
            no_latitude_label.pack(pady =5)
        elif lat_data is not None:
            latitude_label = tk.Label(top, text=f"Latitudes Detected from Variable {latitude_variable_name}") #if successful, displays variable name
            latitude_label.pack(pady=5)
            
        for var in ncx.variables:
            if var in ['lon', 'lons', 'longitude', 'longitudes']: #state common names for lons in files
                lon_data = ncx[var] #if longitude variable found, imports its data to lon_data object for later use
                longitude_variable_name = var
                longitude_found = True
                break
                
        if lon_data == None:
            no_longitude_label = tk.Label(top, text = "No Longitudes Autodetected.") #updates labels if no latitutde or longitude is autodetected
            no_longitude_label.pack(pady =5)
        elif lon_data is not None:
            longitude_label = tk.Label(top, text=f"Longitudes Detected from Variable {longitude_variable_name}")
            longitude_label.pack(pady=5)
            
        auto_next_button = tk.Button(top, text="Next", command=next)
        auto_next_button.pack(pady=5)
    
    else:
        nothing_selected_label = tk.Label(top, text= "Please load a file.", font=(16)) #if no file is loaded, the process does not proceed
        nothing_selected_label.pack(expand=True, fill='both', pady=5)
        
def manual_variable_select(): #STEP 1
    global manual_variable_select_combobox, manual_variable_select_combobox_lon, latitude_found, longitude_found, lat_data, lon_data
    
    manual_variable_select_top_label = tk.Label(top, text = "Manual Select Lat and Lon Variable")
    manual_variable_select_top_label.pack(pady=5)
    
    lat_frame = tk.Frame(top)
    lon_frame = tk.Frame(top)
    
    lat_frame.pack(pady=5, fill = 'both')
    lon_frame.pack(pady=5, fill = 'both')
    
    manual_variable_select_combobox_label = tk.Label(lat_frame, text = "Select Latitude Variable")
    manual_variable_select_combobox_label.pack(side=tk.LEFT, padx=5, pady=10)

    #provides dropdown of all variables within the currently loaded file
    #users select the variable they wish to use to represent latitude and longitude
    manual_variable_select_combobox = Combobox(lat_frame, state="readonly", values = list(ncx.variables))
    manual_variable_select_combobox.pack(pady=10)
    manual_variable_select_combobox.bind("<<ComboboxSelected>>", on_lat_variable_select)
    ToolTip(manual_variable_select_combobox, text="Select the variable corresponding to latitude information in the uploaded data file.")
    
    manual_variable_select_combobox_label_lon = tk.Label(lon_frame, text = "Select Longitude Variable")
    manual_variable_select_combobox_label_lon.pack(side=tk.LEFT, padx=5, pady=10)
    
    manual_variable_select_combobox_lon = Combobox(lon_frame, state="readonly", values = list(ncx.variables))
    manual_variable_select_combobox_lon.pack(pady=10)
    manual_variable_select_combobox_lon.bind("<<ComboboxSelected>>", on_lon_variable_select)
    ToolTip(manual_variable_select_combobox_lon, text="Select the variable corresponding to longitude information in the uploaded data file.")
    
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

    #allows the user to upload files containing lat/lon information using the buttons provided
    lat_file_button = tk.Button(lat_frame, text="Upload File", command=load_lat_file)
    lat_file_button.pack(pady=5)
    ToolTip(lat_file_button, text="Upload a file containing the latitude information for the plot. Format: .csv")
    
    loaded_lat_label = tk.Label(top, text = "Latitude File: None")
    loaded_lat_label.pack(pady=5)
    
    lon_frame.pack(pady=5)
    
    lon_label = tk.Label(lon_frame, text = "Select Longitude File")
    lon_label.pack(side=tk.LEFT, padx=5, pady=10)
    
    lon_file_button = tk.Button(lon_frame, text="Upload File", command=load_lon_file)
    lon_file_button.pack(pady=5)
    ToolTip(lon_file_button, text="Upload a file containing the longitude information for the plot. Format: .csv")
    
    loaded_lon_label = tk.Label(top, text = "Longitude File: None")
    loaded_lon_label.pack(pady=5)
        
    #next button
    next_button = tk.Button(top, text="Next", command=next)
    next_button.pack(pady=5)

#function attached to upload buttons above - displays file explorer and allows selection for latitude file
def load_lat_file():
    global lat_data, latitude_found
    lat_file_path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")]
    )
    lat_data = pd.read_csv(lat_file_path)
    latitude_found = True
    
    if lat_data is not None:
        loaded_lat_label.config(text=f"Latitude File: {lat_file_path}", fg="#32CD32")

#function attached to upload buttons above - displays file explorer and allows selection for longitude file
def load_lon_file():
    global lon_data, longitude_found
    lon_file_path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")]
    )
    lon_data = pd.read_csv(lon_file_path)
    longitude_found = True
    
    if lon_data is not None:
        loaded_lon_label.config(text=f"Longitude File: {lon_file_path}", fg="#32CD32")

#allows the user to manually enter the desired latitude/longitude scale if all other upload options fail
def manual_scale_entry(): 
    global min_lat_entry, max_lat_entry, min_lon_entry, max_lon_entry
    lat_frame = tk.Frame(top)
    lat_frame.pack(pady=5)
    
    min_lat_label = tk.Label(lat_frame, text="Min Lat")
    min_lat_label.pack(side=tk.LEFT, padx=5)
        
    min_lat_entry = tk.Entry(lat_frame)
    min_lat_entry.pack(side=tk.LEFT, padx=5)
    ToolTip(min_lat_entry, text="Specify the minimum latitude for the plot. Accepted latitude format: -90 to 90")
    
    max_lat_label = tk.Label(lat_frame, text="Max Lat")
    max_lat_label.pack(side=tk.LEFT, padx=5)
        
    max_lat_entry = tk.Entry(lat_frame)
    max_lat_entry.pack(side=tk.LEFT, padx=5)
    ToolTip(max_lat_entry, text="Specify the maximum latitude for the plot. Accepted latitude format: -90 to 90")
    
    lon_frame = tk.Frame(top)
    lon_frame.pack(pady=5)
    
    min_lon_label = tk.Label(lon_frame, text="Min Lon")
    min_lon_label.pack(side=tk.LEFT, padx=5)
        
    min_lon_entry = tk.Entry(lon_frame)
    min_lon_entry.pack(side=tk.LEFT, padx=5)
    ToolTip(min_lon_entry, text="Specify the minimum longitude for the plot. Accepted latitude format: -180 to 180")
    
    max_lon_label = tk.Label(lon_frame, text="Max Lon")
    max_lon_label.pack(side=tk.LEFT, padx=5)
        
    max_lon_entry = tk.Entry(lon_frame)
    max_lon_entry.pack(side=tk.LEFT, padx=5)
    ToolTip(max_lon_entry, text="Specify the maximum longitude for the plot. Accepted latitude format: -180 to 180")
    
    #next button (presented as quit button)
    buttons_frame = tk.Frame(top)
    buttons_frame.pack(pady=5)
    
    confirm_button = tk.Button(top, text="Confirm", command=confirm_manual_scale)
    confirm_button.pack(side=tk.LEFT, padx=5)
    
    next_button = tk.Button(top, text="Quit", command=next)
    next_button.pack(side=tk.LEFT, padx=5)

#function to confirm the validity of the scale entered - checks if the entries are numerical and if they are between the valid ranges
#that are specified in the tooltip (-90 to 90 and -180 to 180)
def confirm_manual_scale():
    global min_lat, max_lat, min_lon, max_lon
    global latitude_found, longitude_found
    global lat_data, lon_data
    
    #error checking implemented here to prevent uploading invalid or non-numerical latitude and longitude values
    try:
        #take input values
        min_lat = int(min_lat_entry.get())
        max_lat = int(max_lat_entry.get())
        min_lon = int(min_lon_entry.get())
        max_lon = int(max_lon_entry.get())
        
    except ValueError:
        messagebox.showinfo("Error", "Please enter valid numerical values for latitude and longitude.")
        return
        
        #check lat range
    if not (-90 <= min_lat <= 90) or not (-90 <= max_lat <= 90): #rejects invalid latitude values
        messagebox.showinfo("Error", "Latitude must be between -90 and 90.")
        return
        
        #check lon range
    if not (-180 <= min_lon <= 180) or not (-180 <= max_lon <= 180): #rejects invalid longitude values
        messagebox.showinfo("Error", "Longitude must be between -180 and 180.")
        return
        
    #if all checks passed, update global variables
    latitude_found = True
    longitude_found = True
        
    lat_data = [min_lat, max_lat]
    lon_data = [min_lon, max_lon]

    next() #call next function to check latitude_found and longitude_found again



#ASSIGN COLLECTED LATITUDE/LONGITUDE DATA AND PROCESS IT INTO A USABLE SCALE
#this data will be inputted into generate_plot function to find scale based on netcdf file dimensions
def find_lat_lon_scale():
    global lat_data, lon_data
    
    if isinstance(lat_data, pd.DataFrame):
        lat_data = lat_data.values.flatten()
        print_pink(lat_data.shape)
        
    if isinstance(lon_data, pd.DataFrame):
        lon_data = lon_data.values.flatten()
        print_pink(lon_data.shape)

    #takes the minimum and maximum of the latitude and longitude fields uploaded, no matter the method by which they are specified
    #uses these min/max values alongside the data shape to generate the plot later in the program
    latitudes[0] = min(lat_data)
    latitudes[1] = max(lat_data)
    print(latitudes)
    
    longitudes[0] = min(lon_data)
    longitudes[1] = max(lon_data)
    print(longitudes)
    





#VARIABLE DROPDOWNS#
#assigns selected variable to an object, and sections the data based on selected variable
#collects timestep number from selected variable

#dropdown for selection of main variable to be plotted
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
        messagebox.showinfo("Info", "Selected variable does not have timestep dimension.")
   
#assigns selected mask variable to an object to be used in generate_plot function     
def on_mask_variable_select(event):
    global selected_mask_variable
    selected_mask_variable = mask_variable_dropdown.get()
   
#allows selection of a variable to be used for latitude
def on_lat_variable_select(event):
    global selected_lat_variable
    selected_lat_variable = manual_variable_select_combobox.get()
    
#allows selection of a variable to be used for longitude
def on_lon_variable_select(event):
    global selected_lon_variable
    selected_lon_variable = manual_variable_select_combobox_lon.get()
    
def on_topography_variable_select(event):
    global selected_topography_variable
    selected_topography_variable = topography_variable_dropdown.get()
    
#assigns selected colourmap to an object
def update_colourmap(event):
    global selectedColours
    selectedColours = colourmap_dropdown.get()
    print_pink(f"Selected colourmap: {selectedColours}")
    
    
    
    
    
    
#RADIO BUTTONS AND TOGGLES - SHOW/HIDE PARTS OF UI#
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

#performs the same function but applied to the topography map dropdown
def toggle_topography_dropdown():
    if apply_topography.get():
        topography_variable_dropdown.config(state=tk.NORMAL)
    else:
        topography_variable_dropdown.config(state=tk.DISABLED)
        
        



#LABEL UPDATERS#
#changes the label that shows the current timestep range 
def update_timestep_range():
    if sfc_size is not None:
        timestep_range_label_text.config(text=f"Timestep Range: 0 to {sfc_size-1}")

#changes the label that shows the current loaded file       
def update_loaded_file():
    if ncx is not None:
        loaded_file_label.config(text=f"Loaded File: {file_path}", fg="#32CD32")
        
        


#GIF CREATION#        
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
        
        
def check_input_validity():
    
    if selected_variable and single_timestep_entry.get() is not None and selectedColours:

        if timestep_mode.get() == 1:
            try: #checks whether there is a valid numerical input
                if 0 <= int(single_timestep_entry.get()) <= sfc_size: #checks whether numerical input is in the valid range
                    generate_plot()
                else:
                    messagebox.showerror("Error", "Entered timestep is not within timestep range. Plot cannot be generated.")
                    print("fail beaming")
            except ValueError:
                messagebox.showinfo("Error", "Invalid timestep input. Please enter a numerical input.")
                
            
        
        if timestep_mode.get() == 2: 
            try: #checks whether there is a valid numerical input
                if 0 <= int(start_timestep_entry.get()) <= sfc_size and 0 <= int(end_timestep_entry.get()) <= sfc_size: #checks whether numerical input is in the valid range
                    generate_plot()
                else:
                    messagebox.showerror("Error", "Entered timesteps are not within timestep range. Plot cannot be generated.")
            except ValueError:
                messagebox.showinfo("Error", "Invalid timestep input. Please enter a numerical input.")
    
    else:
        messagebox.showinfo("Error", "Please ensure all paramaters have been specified.")
        
            
        
#PLOT GENERATOR
#generates plot based on timestep and masking options

#this function is structured according to whether a plot (single timestep) or animation (timestep series) should be generated
#within these categories, separate conditions are specified depending on whether the user wishes to apply a data mask or add a topographical map

def generate_plot():
    global selected_variable, selectedColours
    
    if latitudes != [0, 0] and longitudes != [0, 0]:
        
        unit = unit_entry.get()
        
        if not apply_topography.get():

            if not apply_mask.get():
                if timestep_mode.get() == 1:
                    if selected_variable and single_timestep_entry.get() is not None and selectedColours:
                        variable_data = ncx[selected_variable]
                        processed_data = variable_data.isel(sfc=int(single_timestep_entry.get()))
                        
                        lat_count = ncx[selected_variable].shape[1]
                        lon_count = ncx[selected_variable].shape[2]
                        latScale = np.linspace(latitudes[0], latitudes[1], lat_count)
                        lonScale = np.linspace(longitudes[0], longitudes[1], lon_count)

                        fig, ax = plt.subplots(dpi=200, figsize=(10, 10))
                        map = ax.contourf(lonScale, latScale, processed_data.values, cmap=plt.get_cmap(selectedColours))
                        cbar = plt.colorbar(map, ax=ax, label=f'{selected_variable.capitalize()} ({unit})')

                        #axis increments and labels
                        ax.xaxis.set_major_locator(MultipleLocator(2))
                        ax.yaxis.set_major_locator(MultipleLocator(1))
                        ax.set_xlabel('Longitude')
                        ax.tick_params(axis='x', labelsize=7)
                        ax.set_ylabel('Latitude')
                        ax.set_title(f'Plot of variable \'{selected_variable.capitalize()}\' ({unit}) for timestep index: {single_timestep_entry.get()}')

                        #latitude gridlines and greenwich meridian
                        ax.yaxis.grid(True, linestyle='--', alpha=0.7)
                        ax.axvline(x=0, color='red', linestyle='--', linewidth=0.5)
                        
                        print(lonScale)
                        
                        plt.savefig('graph.png')
                        open_image('graph.png')
                
                    else:
                        messagebox.showwarning("Warning", "Please ensure that the variable, timestep, and colourmap are selected.")
                else:
                    
                    if selected_variable and start_timestep_entry.get() and end_timestep_entry.get() is not None and selectedColours:
                        
                        start_timestep = int(start_timestep_entry.get())
                        end_timestep = int(end_timestep_entry.get())
                        
                        all_values = []

                        for timestep in range(start_timestep, end_timestep + 1):
                            flat_data = (ncx.isel(sfc=timestep)[selected_variable]).values.flatten()
                            all_values.extend(flat_data)

                        #calculate the 25th and 75th percentiles
                        percentile_low = np.percentile(all_values, 0.005)
                        percentile_high = np.percentile(all_values, 99.995)

                        print("Lower Percentile:", percentile_low)
                        print("Higher Percentile:", percentile_high)
                        
                        levels = np.linspace(percentile_low, percentile_high, 20)
                        norm = mcolors.Normalize(vmin=percentile_low, vmax=percentile_high)
                        
                        for x in range(start_timestep, (end_timestep+1)):
                            variable_data = ncx[selected_variable]
                            processed_data = variable_data.isel(sfc=x)
                            
                            lat_count = ncx[selected_variable].shape[1]
                            lon_count = ncx[selected_variable].shape[2]
                            latScale = np.linspace(latitudes[0], latitudes[1], lat_count)
                            lonScale = np.linspace(longitudes[0], longitudes[1], lon_count)
                        
                            fig, ax = plt.subplots(dpi=200, figsize=(10, 10))
                            map = ax.contourf(lonScale, latScale, processed_data.values, cmap=plt.get_cmap(selectedColours), levels = levels, norm = norm)
                            cbar = plt.colorbar(map, ax=ax, label=f'{selected_variable.capitalize()} ({unit})')

                            #axis increments and labels
                            ax.xaxis.set_major_locator(MultipleLocator(2))
                            ax.yaxis.set_major_locator(MultipleLocator(1))
                            ax.set_xlabel('Longitude')
                            ax.tick_params(axis='x', labelsize=7)
                            ax.set_ylabel('Latitude')
                            ax.set_title(f'Plot of variable \'{selected_variable.capitalize()}\' ({unit}) for timestep index: {x}')

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
                        masked_data = variable_data.where(combined_mask, drop = False)
                        
                        lat_count = masked_data.shape[0]
                        lon_count = masked_data.shape[1]
                        latScale = np.linspace(latitudes[0], latitudes[1], lat_count)
                        lonScale = np.linspace(longitudes[0], longitudes[1], lon_count)
                        
                        fig, ax = plt.subplots(dpi=200, figsize=(10, 10))
                        map = ax.contourf(lonScale, latScale, masked_data.values, cmap=plt.get_cmap(selectedColours))
                        cbar = plt.colorbar(map, ax=ax, label=f'{selected_variable.capitalize()} ({unit})')

                        #axis increments and labels
                        ax.xaxis.set_major_locator(MultipleLocator(2))
                        ax.yaxis.set_major_locator(MultipleLocator(1))
                        ax.set_xlabel('Longitude')
                        ax.tick_params(axis='x', labelsize=7)
                        ax.set_ylabel('Latitude')
                        ax.set_title(f'Plot of variable \'{selected_variable.capitalize()}\' ({unit}) for timestep index: {single_timestep_entry.get()}')

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
                    
                        all_values = []

                        for timestep in range(start_timestep, end_timestep + 1):
                            flat_data = (ncx.isel(sfc=timestep)[selected_variable]).values.flatten()
                            all_values.extend(flat_data)

                        #calculate the 25th and 75th percentiles
                        percentile_low = np.percentile(all_values, 0.005)
                        percentile_high = np.percentile(all_values, 99.995)

                        print("Lower Percentile:", percentile_low)
                        print("Higher Percentile:", percentile_high)
                        
                        levels = np.linspace(percentile_low, percentile_high, 20)
                        norm = mcolors.Normalize(vmin=percentile_low, vmax=percentile_high, clip=True)
                            
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
                            masked_data = variable_data.where(combined_mask, drop = False)
                            
                            lat_count = masked_data.shape[0]
                            lon_count = masked_data.shape[1]
                            latScale = np.linspace(latitudes[0], latitudes[1], lat_count)
                            lonScale = np.linspace(longitudes[0], longitudes[1], lon_count)
                        
                            fig, ax = plt.subplots(dpi=200, figsize=(10, 10))
                            map = ax.contourf(lonScale, latScale, masked_data.values, cmap=plt.get_cmap(selectedColours), levels = levels, norm = norm)
                            cbar = plt.colorbar(map, ax=ax, label=f'{selected_variable.capitalize()} ({unit})')

                            #axis increments and labels
                            ax.xaxis.set_major_locator(MultipleLocator(2))
                            ax.yaxis.set_major_locator(MultipleLocator(1))
                            ax.set_xlabel('Longitude')
                            ax.tick_params(axis='x', labelsize=7)
                            ax.set_ylabel('Latitude')
                            ax.set_title(f'Plot of variable \'{selected_variable.capitalize()}\' ({unit}) for timestep index: {x}')

                            #latitude gridlines and greenwich meridian
                            ax.yaxis.grid(True, linestyle='--', alpha=0.7)
                            ax.axvline(x=0, color='red', linestyle='--', linewidth=0.5)
                            
                            #save each plot with filename corresponding to x
                            filename = f"plots/plot_{x}.png"
                            print_pink(f"Generated plot {x}")
                            plt.savefig(filename)
                            plt.close(fig) 
                            
                        create_gif()
                        
        if apply_topography.get():
            
            if not apply_mask.get():
                            
                if timestep_mode.get() == 1:
                    
                    if selected_variable and single_timestep_entry.get() is not None and selectedColours:
                        
                        variable_data = ncx[selected_variable]
                        processed_data = variable_data.isel(sfc=int(single_timestep_entry.get()))
                        
                        lat_count = ncx[selected_variable].shape[1]
                        lon_count = ncx[selected_variable].shape[2]
                        latScale = np.linspace(latitudes[0], latitudes[1], lat_count)
                        lonScale = np.linspace(longitudes[0], longitudes[1], lon_count)
                        
                        #TOPOGRAPHICAL VARIABLE
                        topography_data = ncx.isel(sfc=int(single_timestep_entry.get()))[selected_topography_variable]

                        fig, ax = plt.subplots(dpi=200, figsize=(10, 10))
                        map = ax.contourf(lonScale, latScale, processed_data.values, cmap=plt.get_cmap(selectedColours))
                        ax.contour(lonScale, latScale, topography_data.values, cmap = 'Greys')
                        cbar = plt.colorbar(map, ax=ax, label=f'{selected_variable.capitalize()} ({unit})')

                        #axis increments and labels
                        ax.xaxis.set_major_locator(MultipleLocator(2))
                        ax.yaxis.set_major_locator(MultipleLocator(1))
                        ax.set_xlabel('Longitude')
                        ax.tick_params(axis='x', labelsize=7)
                        ax.set_ylabel('Latitude')
                        ax.set_title(f'Plot of variable \'{selected_variable.capitalize()}\' ({unit}) for timestep index: {single_timestep_entry.get()}')

                        #latitude gridlines and greenwich meridian
                        ax.yaxis.grid(True, linestyle='--', alpha=0.7)
                        ax.axvline(x=0, color='red', linestyle='--', linewidth=0.5)
                        
                        print(lonScale)
                        
                        plt.savefig('graph.png')
                        open_image('graph.png')
                
                    else:
                        messagebox.showwarning("Warning", "Please ensure that the variable, timestep, and colourmap are selected.")
                else:
                    
                    if selected_variable and start_timestep_entry.get() and end_timestep_entry.get() is not None and selectedColours:
                        
                        start_timestep = int(start_timestep_entry.get())
                        end_timestep = int(end_timestep_entry.get())
                        
                        all_values = []

                        for timestep in range(start_timestep, end_timestep + 1):
                            flat_data = (ncx.isel(sfc=timestep)[selected_variable]).values.flatten()
                            all_values.extend(flat_data)

                        #calculate the 25th and 75th percentiles
                        percentile_low = np.percentile(all_values, 0.005)
                        percentile_high = np.percentile(all_values, 99.995)

                        print("Lower Percentile:", percentile_low)
                        print("Higher Percentile:", percentile_high)
                        
                        levels = np.linspace(percentile_low, percentile_high, 20)
                        norm = mcolors.Normalize(vmin=percentile_low, vmax=percentile_high)
                        
                        for x in range(start_timestep, (end_timestep+1)):
                            variable_data = ncx[selected_variable]
                            processed_data = variable_data.isel(sfc=x)
                            
                            lat_count = ncx[selected_variable].shape[1]
                            lon_count = ncx[selected_variable].shape[2]
                            latScale = np.linspace(latitudes[0], latitudes[1], lat_count)
                            lonScale = np.linspace(longitudes[0], longitudes[1], lon_count)
                            
                            #topograhical data
                            topography_data = ncx.isel(sfc = x)[selected_topography_variable]
                        
                            fig, ax = plt.subplots(dpi=200, figsize=(10, 10))
                            map = ax.contourf(lonScale, latScale, processed_data.values, cmap=plt.get_cmap(selectedColours), levels = levels, norm = norm)
                            ax.contour(lonScale, latScale, topography_data.values, cmap = 'Greys', alpha = 0.4)
                            cbar = plt.colorbar(map, ax=ax, label=f'{selected_variable.capitalize()} ({unit})')

                            #axis increments and labels
                            ax.xaxis.set_major_locator(MultipleLocator(2))
                            ax.yaxis.set_major_locator(MultipleLocator(1))
                            ax.set_xlabel('Longitude')
                            ax.tick_params(axis='x', labelsize=7)
                            ax.set_ylabel('Latitude')
                            ax.set_title(f'Plot of variable \'{selected_variable.capitalize()}\' ({unit}) for timestep index: {x}')

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
                        masked_data = variable_data.where(combined_mask, drop = False)
                        
                        lat_count = masked_data.shape[0]
                        lon_count = masked_data.shape[1]
                        latScale = np.linspace(latitudes[0], latitudes[1], lat_count)
                        lonScale = np.linspace(longitudes[0], longitudes[1], lon_count)
                        
                        #topograhical data
                        topography_data = ncx.isel(sfc=int(single_timestep_entry.get()))[selected_topography_variable]
                        
                        fig, ax = plt.subplots(dpi=200, figsize=(10, 10))
                        map = ax.contourf(lonScale, latScale, masked_data.values, cmap=plt.get_cmap(selectedColours))
                        ax.contour(lonScale, latScale, topography_data.values, cmap = 'Greys', alpha = 0.4)
                        cbar = plt.colorbar(map, ax=ax, label=f'{selected_variable.capitalize()} ({unit})')

                        #axis increments and labels
                        ax.xaxis.set_major_locator(MultipleLocator(2))
                        ax.yaxis.set_major_locator(MultipleLocator(1))
                        ax.set_xlabel('Longitude')
                        ax.tick_params(axis='x', labelsize=7)
                        ax.set_ylabel('Latitude')
                        ax.set_title(f'Plot of variable \'{selected_variable.capitalize()}\' ({unit}) for timestep index: {single_timestep_entry.get()}')

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
                    
                        all_values = []

                        for timestep in range(start_timestep, end_timestep + 1):
                            flat_data = (ncx.isel(sfc=timestep)[selected_variable]).values.flatten()
                            all_values.extend(flat_data)

                        #calculate the 25th and 75th percentiles
                        percentile_low = np.percentile(all_values, 0.005)
                        percentile_high = np.percentile(all_values, 99.995)

                        print("Lower Percentile:", percentile_low)
                        print("Higher Percentile:", percentile_high)
                        
                        levels = np.linspace(percentile_low, percentile_high, 20)
                        norm = mcolors.Normalize(vmin=percentile_low, vmax=percentile_high, clip=True)
                            
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
                            masked_data = variable_data.where(combined_mask, drop = False)
                            
                            lat_count = masked_data.shape[0]
                            lon_count = masked_data.shape[1]
                            latScale = np.linspace(latitudes[0], latitudes[1], lat_count)
                            lonScale = np.linspace(longitudes[0], longitudes[1], lon_count)
                            
                            #topographical data
                            topography_data = ncx.isel(sfc = x)[selected_topography_variable]
                        
                            fig, ax = plt.subplots(dpi=200, figsize=(10, 10))
                            map = ax.contourf(lonScale, latScale, masked_data.values, cmap=plt.get_cmap(selectedColours), levels = levels, norm = norm)
                            ax.contour(lonScale, latScale, topography_data.values, cmap = 'Greys', alpha = 0.4)
                            cbar = plt.colorbar(map, ax=ax, label=f'{selected_variable.capitalize()} ({unit})')

                            #axis increments and labels
                            ax.xaxis.set_major_locator(MultipleLocator(2))
                            ax.yaxis.set_major_locator(MultipleLocator(1))
                            ax.set_xlabel('Longitude')
                            ax.tick_params(axis='x', labelsize=7)
                            ax.set_ylabel('Latitude')
                            ax.set_title(f'Plot of variable \'{selected_variable.capitalize()}\' ({unit}) for timestep index: {x}')

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
        messagebox.showerror("Error", "Please upload a latitude and longitude scale.")
        
                    




#MAIN FUNCTION#
#this function generates the UI and executes all of the above functions, leading to the running of the program
    
def main():
    global root, variable_dropdown, mask_variable_dropdown, colourmap_dropdown, timestep_range_label_text, timestep_mode, single_timestep_entry, start_timestep_entry, end_timestep_entry
    global ncx, apply_mask, mask_frame, masking_range_start_entry, masking_range_end_entry, loaded_file_label
    global latitude_button, selected_latitude_label, topography_variable_dropdown, unit_entry

    try:
        load_button = tk.Button(root, text="Load File", command=load_file) #button to load data file
        load_button.pack(pady=5)
        ToolTip(load_button, text="Click to load a data file.") 
        
        loaded_file_label = tk.Label(root, text="Loaded File: None") #label that specifies file path of the loaded file once it is updated
        loaded_file_label.pack(pady=5)
        
        latitude_button = tk.Button(root, text="Load Lat/Lon", command=initalise_latitude_popup) #button to initiate process of finding latitude and longitude
        latitude_button.pack(pady=5)
        ToolTip(latitude_button, text="Click to load latitude and longitude data.")
        
        selected_latitude_label = tk.Label(root, text="No lat/lon loaded.") #label that updates with confirmation that lat/lon has been uploaded
        selected_latitude_label.pack(pady=5)

        variable_dropdown_label = tk.Label(root, text="Select Variable:")
        variable_dropdown_label.pack(pady=5)

        variable_dropdown = Combobox(root, state="readonly") #plotting variable selection dropdown menu
        variable_dropdown.pack(pady=5)
        variable_dropdown.bind("<<ComboboxSelected>>", on_variable_select)
        ToolTip(variable_dropdown, text="Select variable from the data to be plotted. If dropdown is empty, please check that a file is loaded.")
        
        #provide entry field for manual unit entry for unit corresponding to selected plotting variable above
        unit_frame = tk.Frame(root) 
        unit_frame.pack(pady=5)
        
        unit_entry_label = tk.Label(unit_frame, text="Enter Plotting Variable Unit:")
        unit_entry_label.pack(side=tk.LEFT, padx=5)
        
        unit_entry = tk.Entry(unit_frame)
        unit_entry.pack(side=tk.LEFT, padx=5)
        
        #label the radio buttons for selecting single timestep or timestep series (production of plot or animation)
        timestep_range_label = tk.Label(root, text="Select Single Timestep or Range:")
        timestep_range_label.pack(pady=5)
        
        #add radio buttons for single timestep and timestep series
        #deactivate timestep entry fields corresponding to the mode which is not selected
        timestep_mode = tk.IntVar(value=1) #define the variable that the radio buttons change
        single_timestep_radio = tk.Radiobutton(root, text = "Single Timestep", variable = timestep_mode, value = 1, command = toggle_timestep_mode)
        single_timestep_radio.pack(pady=5)
        double_timestep_radio = tk.Radiobutton(root, text = "Timestep Range", variable = timestep_mode, value = 2, command = toggle_timestep_mode)
        double_timestep_radio.pack(pady=5)
        
        single_frame = tk.Frame(root)
        single_frame.pack(pady=5)
        
        single_timestep_label = tk.Label(single_frame, text="Enter Single Timestep:")
        single_timestep_label.pack(side=tk.LEFT, padx=5)
        
        single_timestep_entry = tk.Entry(single_frame) #enter single timestep
        single_timestep_entry.pack(pady=5)
        ToolTip(single_timestep_entry, text="Enter the single timestep frame to be displayed in the plot. Available timestep range is displayed below when a plotting variable is selected.")
        
        range_frame = tk.Frame(root)
        range_frame.pack(pady=5)
        
        start_timestep_label = tk.Label(range_frame, text="Start Timestep")
        start_timestep_label.pack(side=tk.LEFT, padx=5)
        
        start_timestep_entry = tk.Entry(range_frame) #enter starting timestep for timestep range
        start_timestep_entry.pack(side=tk.LEFT, padx=5)
        ToolTip(start_timestep_entry, text="Enter the timestep at which to begin the animation. Available timestep range is displayed below when a plotting variable is selected.")
        
        end_timestep_label = tk.Label(range_frame, text="End Timestep")
        end_timestep_label.pack(side=tk.LEFT, padx=5)
        
        end_timestep_entry = tk.Entry(range_frame) #enter ending timestep for timestep range
        end_timestep_entry.pack(side=tk.LEFT, padx=5)
        ToolTip(end_timestep_entry, text="Enter the timestep at which to terminate the animation. Available timestep range is displayed below when a plotting variable is selected.")
        
        timestep_range_label_text = tk.Label(root, text="Timestep Range: N/A")
        timestep_range_label_text.pack(pady=5)
        
        toggle_timestep_mode()
        
        #add mask applying toggle
        apply_mask_toggle = tk.Checkbutton(root, text = "Apply Mask?", variable = apply_mask, command = toggle_masking_mode)
        apply_mask_toggle.pack(pady=5)
        ToolTip(apply_mask_toggle, text="Toggles data masking on produced plot. Mask application to the plot hides data within a specified range for a selected variable found within the uploaded file.")
        
        #add frame for masking options
        mask_frame = tk.Frame(root)
        mask_frame.pack(pady=5)
        
        mask_variable_dropdown_label = tk.Label(mask_frame, text="Masking Variable:")
        mask_variable_dropdown_label.pack(side=tk.LEFT, padx=5)
        
        mask_variable_dropdown = Combobox(mask_frame, state="readonly") #select variable with which to construct the data mask
        mask_variable_dropdown.pack(side=tk.LEFT, pady=5)
        mask_variable_dropdown.bind("<<ComboboxSelected>>", on_mask_variable_select) #assigns the selected variable to 'selected_mask_variable'
        ToolTip(mask_variable_dropdown, text="Select variable relevant to the construction of the desired mask. Selection of the variable corresponding to ice thickness is suggested.")

        masking_range_start_label = tk.Label(mask_frame, text="Range Start:")
        masking_range_start_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        masking_range_start_entry = tk.Entry(mask_frame)
        masking_range_start_entry.pack(side=tk.LEFT, pady=5)
        
        masking_range_end_label = tk.Label(mask_frame, text="Range End:")
        masking_range_end_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        masking_range_end_entry = tk.Entry(mask_frame)
        masking_range_end_entry.pack(side=tk.LEFT, pady=5)
        
        toggle_masking_mode()

        #add options for generating topography map
        topography_frame = tk.Frame(root)
        topography_frame.pack(pady=5)
        
        apply_topography_toggle = tk.Checkbutton(topography_frame, text = "Apply Topograhical Map?", variable = apply_topography, command = toggle_topography_dropdown)
        apply_topography_toggle.pack(pady=5)
        ToolTip(apply_topography_toggle, text="Toggles display of topographical map on the produced plot. Requires uploaded data to contain a variable corresponding to base topography.")
        
        topography_label = tk.Label(topography_frame, text="Topography Map:")
        topography_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        topography_variable_dropdown = Combobox(topography_frame, state="readonly") #select variable from which to generate the topography map
        topography_variable_dropdown.pack(side=tk.LEFT, padx=5, pady=5)
        topography_variable_dropdown.bind("<<ComboboxSelected>>", on_topography_variable_select)
        ToolTip(topography_variable_dropdown, text="Select variable corresponding to map of base topography in the uploaded data file.")
        
        toggle_topography_dropdown()

        #options for selecting plot colourmap
        colourmap_label = tk.Label(root, text="Select Colourmap")
        colourmap_label.pack(pady=5)

        colourmap_dropdown = Combobox(root, state="readonly", values=list(colormaps)) #dropdown for specifying colourmap
        colourmap_dropdown.pack(pady=5)
        colourmap_dropdown.bind("<<ComboboxSelected>>", update_colourmap)
        ToolTip(colourmap_dropdown, text="Select the matplotlib colourmap to be applied to the generated plot.")

        generate_plot_button = tk.Button(root, text="Generate Plot", command=check_input_validity)
        generate_plot_button.pack(pady=10)

        root.protocol("WM_DELETE_WINDOW", on_close)  #handle window close

        root.mainloop()

    except Exception as e:
        print(f"An error occurred: {e}")
        
main()
