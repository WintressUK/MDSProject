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
            print_pink(f'Error loading file.')
         
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

#changes the label that shows the current timestep range 
def update_timestep_range():
    if sfc_size is not None:
        timestep_range_label_text.config(text=f"Timestep Range: 0 to {sfc_size-1}")

#changes the label that shows the current loaded file       
def update_loaded_file():
    if ncx is not None:
        loaded_file_label.config(text=f"Loaded File: {file_path}")

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

    try:
        negis_lats = pd.read_csv("latbook.csv", header=None)
        negis_lons = pd.read_csv("lonbook.csv", header=None)

        load_button = tk.Button(root, text="Load File", command=load_file)
        load_button.pack(pady=20)
        
        loaded_file_label = tk.Label(root, text="Loaded File: None")
        loaded_file_label.pack(pady=5)

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