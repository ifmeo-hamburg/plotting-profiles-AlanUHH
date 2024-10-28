import matplotlib.pyplot as plt
import gsw
import numpy as np
import xarray as xr
import os
import matplotlib as mpl
mpl.use('TkAgg')
from matplotlib import rcParams

config = {
    "font.family": 'Times New Roman',  # 设置字体类型
    "axes.unicode_minus": False  # 解决负号无法显示的问题
}
rcParams.update(config)


from matplotlib.ticker import ScalarFormatter

# For these to work, you need to install CTD-tools (https://gitlab.rrz.uni-hamburg.de/ifmeo/processing/ctd-tools)
from ctd_tools.modules.reader import CnvReader, NetCdfReader
from ctd_tools.modules.writer import NetCdfWriter
from ctd_tools.modules.plotter import CtdPlotter

# Input file paths
cnv_file_with_path = 'E:/黄志坤/Master/course/Observational Methods and Remote Sensing/exercise/exercise1-final/data/MSM121_054_1db.cnv'

# Output file paths for netCDF
netcdf_file_with_path = 'E:/hzk/MSM121_054_1db.nc'
netcdf_file_with_path_edited = 'E:/hzk/MSM121_054_1db_edited.nc'

# Output file paths for figures
figdir = 'E:/hzk/figure/'
if not os.path.exists(figdir):
    os.makedirs(figdir)

# Using pyCNV
# Data from Seabird sensors typically come in as .cnv files.
# These files can be converted to netCDF format using the seabird package.
# In this case, we've done the conversion for you.

# converted cnv to netcdf (MSM121_054_1db.cnv --> MSM121_054_1db.nc) on the command line

# Instead of using seabird package on CLI for conversion:
# do it here within Python, but check before whether the .nc file already exists using os package
#if not os.path.exists(netcdf_file_with_path):
#    data = fCNV(cnv_file_with_path) # read .cnv file
#    cnv2nc(ds, netcdf_file_with_path) # write .nc file

# Using ctd-tools
# Read CTD data from CNV file
reader = CnvReader(cnv_file_with_path)
dataset = reader.get_data()

# Write dataset with CTD data to netCDF file
writer = NetCdfWriter(dataset)
if not os.path.exists(netcdf_file_with_path):
    writer.write(netcdf_file_with_path)

# load data
ctd_ds = xr.open_dataset(netcdf_file_with_path)

# print data
print(ctd_ds.info)

# Here we are defining the names of the variables in the netCDF file
# If your netcdf file calls salinity "PSAL", you would change the sal_string to 'PSAL'
sal_string = 'salinity'
temp_string = 'temperature'
pres_string = 'pressure'
lon_string = 'longitude'
lat_string = 'latitude'
SA_string = 'absolute_salinity'
CT_string = 'conservative_temperature'
z_string='depth'
# You could also define these pairs in a dictionary (https://www.w3schools.com/python/python_dictionaries.asp)

# To initialise a figure, use matplotlib.plt.figure() which takes inputs within the brackets
# Since matplotlib is long to write, in the import cell above, we've imported it as plt
plt.figure(1, figsize=(12, 8))

# In case the figure 1 already exists, clear it using clf()
plt.clf()

# Within the figure window, we'll actually have two separate sets of axes.  These are called 'subplots' in matplotlib
# We'll have two subplots, one next to the other, so we'll have a 1x2 grid of subplots
plt.subplot(1,2,1)

# To plot salinity, we need to reference the salinity variable in the dataset.  This is done using the syntax ctd_ds['PSAL2']
# Here, ctd_ds is the name of the dataset, and 'PSAL2' is the name of the variable.  The variable name is case sensitive.
plt.plot(ctd_ds[sal_string], ctd_ds[pres_string], color='blue')

# Now we'd like to annotate our figure.  We can do this using the plt.xlabel() and plt.ylabel() functions
# These functions take a string as an argument, which is the text that will be displayed on the x and y axes
# An optional second argument can be used to specify the fontsize.  IMPORTANT: choose values to make the text readable.
plt.xlabel('Practical salinity[]' , fontsize=12,)
plt.ylabel('Pressure [dbar]', fontsize=12)

# Since pressure decreases with depth, we want to invert the y-axis so that the surface is at the top of the plot
plt.ylim([0,3600])
plt.gca().invert_yaxis()

# Here we specify where exactly the x-ticks should be placed.  We want them at 34, 34.5, and 35
x_ticks = [34,34.25, 34.5,34.75, 35]
plt.xticks(x_ticks, fontsize=12)

# We don't specify for the y-axis, but we do want the text size to be readable.
y_ticks=[0,1000,2000,3000]
plt.yticks(y_ticks,fontsize=12)

# Finally, we can add a title to the plot using plt.title().  This function also takes a string as an argument.
plt.title('Salinity profile', fontsize=18)
plt.grid(True,linestyle=":")

# YOUR TURN: Now, let's plot the temperature profile on the right-hand side of the figure

plt.subplot(1,2,2)
plt.plot(ctd_ds[temp_string], ctd_ds[pres_string], color='red')
plt.xlabel('Temperature[℃]' , fontsize=12)
plt.ylabel('Pressure [dbar]', fontsize=12)
plt.ylim([0,3600])
plt.gca().invert_yaxis()
x_ticks = [0,5,10,15]
plt.xticks(x_ticks, fontsize=12)
y_ticks=[0,1000,2000,3000]
plt.yticks(y_ticks,fontsize=12)
plt.title('Temperature profile', fontsize=18)
plt.grid(True,linestyle=":")

# This code saves the figure to a file.  The file type is determined by the extension of the filename.
# Change LastName to your last name
plt.savefig(figdir + 'ex1fig1-Huang-Messfern.png')
plt.show()

# Calculate absolute salinity
SA_2 = gsw.conversions.SA_from_SP(ctd_ds[sal_string],ctd_ds[pres_string],ctd_ds[lon_string],ctd_ds[lat_string])

# Calculate conservative temperature
CT_2 = gsw.conversions.CT_from_t(SA_2,ctd_ds[temp_string],ctd_ds[pres_string])

type(SA_2)
# Add the new variables to the dataset
# Here we've included scan as a `dimension` for the new variables which is required for the data format netCDF
ctd_ds['absolute_salinity'] = (("time"), SA_2.values)
ctd_ds['absolute_salinity'].attrs['long_name'] = 'Absolute Salinity [g/kg]'
ctd_ds['conservative_temperature'] = (("time"), CT_2.values)
ctd_ds['conservative_temperature'].attrs['long_name'] = 'Conservative Temperature [°C]'
# Note in the lines above, to add a new variable to the dataset, we use the syntax ctd_ds['variable_name'] = (dimensions, data)
# Since the dimensions of the previous variables were (time), we need to include these dimensions for the new variables as well
# The .values attribute is used to extract the data from the xarray DataArray object

# Check the data.  Note that the new variables are now in the dataset.
print(ctd_ds.info)

# Your code here

## Plot the absolute salinity and conservative temperature profiles against depth in meters.

depth=gsw.conversions.z_from_p(ctd_ds[pres_string],ctd_ds[lat_string])
ctd_ds['depth'] = (("time"), depth.values)
ctd_ds['depth'].attrs['long_name'] = 'Depth [m]'

plt.figure(2, figsize=(12, 8))
plt.clf()
plt.subplot(1,2,1)
plt.plot(ctd_ds[sal_string], -ctd_ds[z_string], color='blue')
plt.xlabel('Practical salinity[]' , fontsize=12)
plt.ylabel('Depth [m]', fontsize=12)
plt.ylim([0,3600])
plt.gca().invert_yaxis()
x_ticks = [34,34.25,34.5,34.75,35]
plt.xticks(x_ticks, fontsize=12)
y_ticks=[0,1000,2000,3000]
plt.yticks(y_ticks,fontsize=12)
plt.title('Salinity profile', fontsize=18)
plt.grid(True,linestyle=":")

plt.subplot(1,2,2)
plt.plot(ctd_ds[CT_string], -ctd_ds[z_string], color='red')
plt.xlabel('Conservative temperature[℃]' , fontsize=12)
plt.ylabel('Depth [m]', fontsize=12)
plt.ylim([0,3600])
plt.gca().invert_yaxis()
x_ticks = [0,5,10,15]
plt.xticks(x_ticks, fontsize=12)
y_ticks=[0,1000,2000,3000]
plt.yticks(y_ticks,fontsize=12)
plt.title('Conservative temperature profile', fontsize=18)
plt.grid(True,linestyle=":")

plt.savefig(figdir + 'ex1fig2-Huang-Messfern.png')
plt.show()

ctd_ds.to_netcdf(netcdf_file_with_path_edited)

#https://stackoverflow.com/questions/41634179/matplotlib-contour-lines-are-not-closing-up

# On a TS diagram, the X axis is salinity and the Y axis is temperature.
# As a helpful reminder, we can create variables X and Y.
x = ctd_ds[SA_string]
y = ctd_ds[CT_string]


# A typical TS diagram also has contours of potential density.  We can add these using the gsw package.
# meshgrid creates a grid of points for the contour plot.  The first two arguments are the x and y values,
xa=np.linspace(min(x.values),max(x.values),100)
ya=np.linspace(min(y.values),max(y.values),100)
X, Y = np.meshgrid(xa, ya)
# The third argument is the potential density, which is calculated using the gsw.density.sigma0() function
Z = gsw.density.sigma0(X, Y)

# Now we can plot the data.  We'll use the plt.plot() function for the curve with temperature and salinity, which takes the x and y values as arguments.
plt.figure(3,figsize=(5, 8))
plt.plot(x,y, color='green', marker='o', markersize='6')
plt.xlabel('Absolute Salinity[]', fontsize=14)
plt.ylabel(' Temperature [°C]', fontsize=14)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.ylim(1.5,14.4)
plt.title('TS diagram', fontsize=18)

# Then we add contours using the plt.contour() function.  This function takes the X, Y, and Z values as arguments.
CS = plt.contour(X, Y, Z, 10, colors='grey', zorder=2)
plt.clabel(CS, inline=True, fontsize=12)

plt.grid(True)
# Change Lastname to your last name
plt.savefig(figdir + 'ex1fig3-Huang-Messfern.png')
plt.show()



plt.figure(4,figsize=(8, 8))
CS = plt.contour(X, Y, Z, 10, colors='grey', zorder=2)
plt.clabel(CS, inline=True, fontsize=12)
plt.plot(x,y, color='red', marker='o', markersize='6')
plt.xlabel('Absolute Salinity[]', fontsize=14)
plt.ylabel(' Temperature [°C]', fontsize=14)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.ylim(1.5,9)
plt.title('TS diagram', fontsize=18)
plt.grid(False)
plt.savefig(figdir + 'ex1fig4-Huang-Messfern.png')
plt.show()