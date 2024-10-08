Welcome to the supplementary repository for the MDS Project "A Python Tool for Visualisation of Ice Sheet Model Data in netCDF Format".

The provided plotting tool can be accessed by viewing the file "PlottingTool.py" within this repository.

The required Python packages for the provided software tool are as follows:
* sys
* matplotlib
* xarray
* numpy
* pandas
* tkinter
* os
* platform
* glob
* Pillow
* scipy
* ttkbootstrap

This project was built using example ice sheet model output data from the BISICLES model for the North East Greenland Ice Stream region. A small subsection of the data used can be found within this repository in the file
'GreenlandData.nc'.
This data is intended for basic testing of the plotting tool, and only includes one variable and timestep.

The latitudes and longitudes to be imported into the plotting tool alongside the test file can be found in the .csv files titled 'latbook' and 'lonbook'. These can be imported using the 'Upload Lat/Lon File' menu.

The animations provided in this repository supplement the static images provided in the 'Results' section of the project report, and are named according to their corresponding figure in the report.

