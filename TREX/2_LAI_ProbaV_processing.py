#           ProbaV - LAI processing tool
#                 (25/04/2018)
#-------------------------------------------------------
# - - - MODULES AND WORKING DIRECTORIES - - - - - - - - -
#-------------------------------------------------------

import os
import gdal
import pandas as pd
import numpy as np
from IPython import get_ipython
import shutil

#-------------------------------------------------------
# - - - INITIATE SETUP - - - - - - - - - - - - - - - - -
#-------------------------------------------------------
current_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(current_dir)

setup_name = "LAI_ProbaV_setup.txt"
read_setup = open(setup_name,'r')
print read_setup

# skip first 5 lines
for i in range(5):
    read_setup.readline()
# read line #6 reference raster
reference_raster = read_setup.readline().split()
dir_input_raster = current_dir + "\\reference_maps\\" + reference_raster[-1]

# skip line #7 
read_setup.readline()
# read line #8 cloud fraction
cloud_fraction = read_setup.readline().split()
f_invalid_px_1 = cloud_fraction[-1]
# read line #9 wipe out 
step1 = read_setup.readline().split()
step1 = int(step1[-1])
# skip line #10-11
for i in range(2):
    read_setup.readline()
# read line #12 
step2 = read_setup.readline().split()
step2 = int(step2[-1])
# read line #13
step3 = read_setup.readline().split()
step3 = int(step3[-1])
# read line #14 
step4 = read_setup.readline().split()
step4 = int(step4[-1])
# read line #15 
step5 = read_setup.readline().split()
step5 = int(step5[-1])
# read line #16 
step6 = read_setup.readline().split()
step6 = int(step6[-1])
# read line #17 
step7 = read_setup.readline().split()
step7 = int(step7[-1])

dir_input_maps = current_dir + "\\probaV_download"
dir_step2 = current_dir + "\\main\\1_NDVI_tif"
dir_step3 = current_dir + "\\main\\2_LAI_tif"
dir_step4 = current_dir + "\\main\\3_LAI_asc"
dir_step5 = current_dir + "\\main\\4_monthly_LAI_tif"
dir_step6 = current_dir + "\\main\\5_monthly_LAI_asc"
dir_step7 = current_dir + "\\main\\6_inter_LAI_asc"
temp = current_dir + "\main\\temp"

#-------------------------------------------------------
# - - - FUNCTIONS - - - FUNCTIONS - - - FUNCTIONS - - -
#-------------------------------------------------------

def SearchFolder(directory, file_type):
# Checks the content of a folder (%directory) for a defined type of files (%file_type eg. ".tif")
# and returns a list of those files
    MyFolder = os.listdir(directory)
    MyList = []
    a = len(file_type)
    for b in range(len(MyFolder)):
        i = MyFolder[b]
        if i[-a:] == file_type :
            MyList.append(MyFolder[b])
    return MyList

def CopyClearTemp(moveFrom, moveTo):
# copy from the temporal directory       
    tempFiles=SearchFolder(moveFrom, '.tif')        
    for i in range (len(tempFiles)):
        in_raster = moveFrom + "\\" + tempFiles[i]
        out_raster = moveTo + "\\" + tempFiles[i]
        shutil.copy2(in_raster, out_raster)
# clear the temporal directory            
    rerun = [moveFrom]
    for i in range(len(rerun)):
        files = os.listdir(rerun[i])
        path = rerun[i]
        for i in range(len(files)):
            os.remove(path + "/" + files[i])     

def JustCopy(moveFrom, moveTo):
# copy from the temporal directory       
    tempFiles=SearchFolder(moveFrom, '.tif')        
    for i in range (len(tempFiles)):
        in_raster = moveFrom + "\\" + tempFiles[i]
        out_raster = moveTo + "\\" + tempFiles[i]
        shutil.copy2(in_raster, out_raster)
        
def PixelsQuality(NDVI,SM,output_folder,filename,f_invalid_px):
#def PixelsQuality(NDVI, SM ,output_folder, filename):
# Applys status maps (from a given directory %SM) to creates cloudless/shadowless 
# new ndvi.tif maps from downloaded ProbaV NDVI images (from a giver directory %NDVI) at 
# selected directory (%output_folder) using a list of names (%filename). Images with
# a certain % of invalid pixels (%f_invalid_px) are not processed.
    
# 0001 1111 = 248 clear, inland, all radiometric is ok
# 0001 0111 = 232 clear, inland, no SWIR
# 0001 1110 = 120 clear, inland, no BLUE
# 0001 0110 = 104 clear, inland, no SWIR, no BLUE
# 0000 1111 = 240 clear, sea, all radiometric is ok    
# 1001 1111 = 249 inland, ice / snow
# 0111 1111 = 254 inland, cloud
# 0011 1111 = 252 inland, shadow

    NDVI_source = gdal.Open(NDVI)
    band_info_NDVI= NDVI_source.GetRasterBand(1)
    xSize = band_info_NDVI.XSize
    ySize = band_info_NDVI.YSize
    nodata= band_info_NDVI.GetNoDataValue()
    geoTrans = NDVI_source.GetGeoTransform()
    wktProjection = NDVI_source.GetProjection() 
    band_Array_NDVI = np.array(gdal.Band.ReadAsArray(band_info_NDVI))
    SM_source = gdal.Open(SM)
    band_info_SM = SM_source.GetRasterBand(1)  
    band_Array_SM = np.array (gdal.Band.ReadAsArray(band_info_SM))
    SM_invalid_pixels = zip(*np.where ((band_Array_SM != 248) & (band_Array_SM != 232) & (band_Array_SM != 120) & (band_Array_SM != 104)))
#    SM_invalid_pixels = zip(*np.where (band_Array_SM != 248))
    counter = 0
    pixels = xSize*ySize
# % of clouds, above this threshold image will be discarded   
    for i in SM_invalid_pixels:
        band_Array_NDVI[i]=nodata
        counter += 1
#Test for clouds   
    if counter > pixels*f_invalid_px:
        pass
    else:  
        os.chdir (output_folder)
#        new_filename = "Valid_NDVI_100m_" + filename + ".tif"
        driver = gdal.GetDriverByName('GTiff')
#        dataset = driver.Create(new_filename,xSize, ySize, 1)
        dataset = driver.Create(filename,xSize, ySize, 1, gdal.GDT_Float32)
        dataset.SetGeoTransform(geoTrans)
        dataset.SetProjection(wktProjection)
        oBand = dataset.GetRasterBand(1)
        oBand.SetNoDataValue(nodata)
        oBand.WriteArray(band_Array_NDVI)    
        #Cleaning Memory
        del dataset
        del NDVI_source
        del SM_source
    
def NDVI_conversion(image_input,output_folder,filename):
# Converts NDVI images (from a given directory %image_input) from digital values to physical 
# values and saves at selected directory (%output_folder) using list of names (%filename)
    data_src = gdal.Open(image_input)
    band_info = data_src.GetRasterBand(1)
    xSize = band_info.XSize
    ySize = band_info.YSize
    nodata=band_info.GetNoDataValue()
    geoTrans = data_src.GetGeoTransform()
    wktProjection = data_src.GetProjection() 
    band_Array = gdal.Band.ReadAsArray(band_info)
    Multiplied_band_Array= (band_Array * 0.004) - 0.08
    Multiplied_band_Array_Nodata=np.where(band_Array == nodata, nodata, Multiplied_band_Array)
    os.chdir (output_folder)
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(filename, xSize, ySize, 1, gdal.GDT_Float32)
    dataset.SetGeoTransform(geoTrans)
    dataset.SetProjection(wktProjection)
    oBand = dataset.GetRasterBand(1)
    oBand.SetNoDataValue(nodata)
    oBand.WriteArray(Multiplied_band_Array_Nodata)
    del dataset
    del data_src

def NDVI_correction(image_input,output_folder,filename):
# Corrects the offset value from conversion equation: (NDVI*0.004)-0.08
    data_src = gdal.Open(image_input)
    band_info = data_src.GetRasterBand(1) #There's only the one band
    xSize = band_info.XSize
    ySize = band_info.YSize
    nodata=band_info.GetNoDataValue()
    geoTrans = data_src.GetGeoTransform()
    wktProjection = data_src.GetProjection() 
    band_Array = gdal.Band.ReadAsArray(band_info)
    band_Array_NDVI_less_than_0_Values= zip(*np.where (band_Array < 0))
    for i in band_Array_NDVI_less_than_0_Values:
        band_Array[i]=0
#        band_Array[i]=nodata
    os.chdir (output_folder)
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(filename, xSize, ySize, 1, gdal.GDT_Float32 )
    dataset.SetGeoTransform(geoTrans)
    dataset.SetProjection(wktProjection)
    oBand = dataset.GetRasterBand(1)
    oBand.SetNoDataValue(nodata)
    oBand.WriteArray(band_Array)
#    data_src = None
    del dataset
    del data_src
    
def GetCellSize(path):
#Returns raster's (given %path) cellsize (x, y)
    data_src = gdal.Open(path)
    data_geo = data_src.GetGeoTransform()
    xres = data_geo[1]
    yres = data_geo[5]
    return xres, yres
    del data_src

def GetExtent(path):
#Returns raster's (given %path) extent where l/u is lower/upper and l/r is left/right
    data_src = gdal.Open(path)
    data_geo = data_src.GetGeoTransform()
    xll = data_geo[0]
    yul = data_geo[3]
    data_src = data_src.GetRasterBand(1)
    ncols = data_src.XSize
    nrows = data_src.YSize
    xlr = xll + data_geo[1]*ncols
    yll = yul - data_geo[1]*nrows
#    nodata=data_src.GetNoDataValue()
    return xll, yll, xlr, yul, ncols, nrows
    del data_src
    
def LAI_Map_Tiff(image_input,output_folder,filename):
#Computes LAI.tif map (output folder) based on NDVI.tif (image_input) using filename
    data_src = gdal.Open(image_input)
    band_info = data_src.GetRasterBand(1) 
    xSize = band_info.XSize
    ySize = band_info.YSize
    nodata = band_info.GetNoDataValue()
    geoTrans = data_src.GetGeoTransform()
    wktProjection = data_src.GetProjection() 
    ndvi_map = gdal.Band.ReadAsArray(band_info)
#    masked_ndvi=np.ma.masked_equal(ndvi_map, nodata).mean(axis=0)
    
#   silence comment about SQRT... it depends on your python/spyder version or envir paths...
    np.seterr(divide='ignore', invalid='ignore')    
    #LAI Formula - Su
    LAI_map = np.sqrt(ndvi_map * (1+ndvi_map) / (1-ndvi_map))   
    
    save_LAI_map_Nodata=np.where(ndvi_map == nodata, nodata, LAI_map)

    
    # providing new filename for new images
    os.chdir (output_folder)
    new_filename = "LAI_Map_" + filename + ".tif" 
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(new_filename, xSize, ySize, 1, gdal.GDT_Float32)
    dataset.SetGeoTransform(geoTrans)
    dataset.SetProjection(wktProjection)
    oBand = dataset.GetRasterBand(1)
    oBand.SetNoDataValue(nodata)
#    oBand.WriteArray(LAI_map)
    oBand.WriteArray(save_LAI_map_Nodata)
    
#    Cleaning Memory
    del dataset

def LAI_Map_Agg(in_raster,output_folder,filename, month, year, xarray, yarray):
   
    list_of_maps = []
    for i in filename:
        if i[-8:-2] == year+month: list_of_maps.append(i)
    print list_of_maps
#looping through selected month and year!
    if len(list_of_maps) == 0:
        pass
    else:
#create i - dimentional matrix per month
        LAI_maps = []
        for i in range(len(list_of_maps)):
            image_input = in_raster + "\\" + list_of_maps[i] + ".tif"

            data_src = gdal.Open(image_input)
            band_info = data_src.GetRasterBand(1)
            xSize = band_info.XSize
            ySize = band_info.YSize
            nodata = band_info.GetNoDataValue()
            geoTrans = data_src.GetGeoTransform()
            wktProjection = data_src.GetProjection() 
            add_array = np.array(gdal.Band.ReadAsArray(band_info))
            LAI_maps.append(add_array)        
        LAI_maps_unmasked = np.where(LAI_maps == nodata, nodata, np.array(LAI_maps))        
        LAI_maps_masked = np.ma.masked_equal(LAI_maps_unmasked, nodata).mean(axis=0)
        Avg_LAI = np.array(LAI_maps_masked)

        df=pd.DataFrame(Avg_LAI)
        df[df == nodata] = nodata
        filled_df=df.fillna(np.nanmean(df))
        final_df=np.where(filled_df == 0, nodata, filled_df)  
        save_LAI_maps=np.array(final_df) 
        
# a version with clipped map!        
        border = gdal.Open(dir_input_raster)
        band_info = border.GetRasterBand(1) 
        xSize = band_info.XSize
        ySize = band_info.YSize
        nodata = band_info.GetNoDataValue()
        geoTrans = data_src.GetGeoTransform()
        wktProjection = data_src.GetProjection() 
        border_raster = gdal.Band.ReadAsArray(band_info)
        save_LAI_maps_unmasked = np.where(border_raster == nodata, nodata, np.array(save_LAI_maps))

        os.chdir(output_folder)
        name = list_of_maps[0]
        date = name[-8:-2]
        image_output = output_folder + "\\Monthly_LAI_" + str(date) + ".tif" 

        driver = gdal.GetDriverByName('GTiff')
        dataset = driver.Create(image_output, xSize, ySize, 1, gdal.GDT_Float32)
        dataset.SetGeoTransform(geoTrans)
        dataset.SetProjection(wktProjection)
        oBand = dataset.GetRasterBand(1)
        oBand.SetNoDataValue(nodata)
        
#        oBand.WriteArray(save_LAI_maps)
#        clipped version
        oBand.WriteArray(save_LAI_maps_unmasked)
        del dataset

def LAI_interpolation(input_pre, input_x,input_nxt, output_folder,filename):
    pass

def filler(file):
    pass
        
#-------------------------------------------------------
# - - - MAIN - - - MAIN - - - MAIN - - - MAIN - - -
#-------------------------------------------------------

#---------------------------------------------
# - - - STEP 1 - - - STEP 1 - - - STEP 1 - - -
#---------------------------------------------
# STEP 1: Delete all files from previous runs. 
# Highly recommended after changing dataset (new maps etc.)
            
if step1 == 1:
#    print '\n STEP 1'
    print '\nDeleting old content...'           
    rerun = [dir_step2, dir_step3, dir_step4, dir_step5, dir_step6, dir_step7, temp]
    for i in range(len(rerun)):
        files = os.listdir(rerun[i])
        path = rerun[i]
        for i in range(len(files)):
            os.remove(path + "//" + files[i])            
else:
    pass
#---------------------------------------------
# - - - STEP 2 - - - STEP 2 - - - STEP 2 - - -
#---------------------------------------------
# STEP 2: Main processing. 
if step2 == 1:    
#    print '\n STEP 2'
#    print 'Checking radiometric and state quality. Discarding images with ' +  str(f_invalid_px_1*100) + '% or more invalid pixels...'
    print '\nChecking radiometric quality...'
    NDVI_list = []
    NDVI_list = SearchFolder(dir_input_maps, 'NDVI.tif')
    SM_list = []
    SM_list = SearchFolder(dir_input_maps, 'SM.tif')    
    fNames = []
    for i in range (len(NDVI_list)):
        breaklist = NDVI_list[i].split(".")
        fn = breaklist [0].split("_")[-4]
        fn = fn + "_NDVI.tif"
        fNames.append(fn)
    for i in range (len(NDVI_list)):
        os.chdir (dir_input_maps)
        Cloud_Free_Image = PixelsQuality(NDVI_list[i],SM_list[i],temp, fNames[i], f_invalid_px_1)   
    CopyClearTemp(temp, dir_step2)       
#---------------------------------------------
    print '\nConversion from digital values to physical values...'
    Myfiles22= SearchFolder(dir_step2, 'NDVI.tif')    
# After discarding !!!   
    filenames = []
    dates = []
    for i in range (len(Myfiles22)):
        breaklist = Myfiles22[i].split(".")
        fn = breaklist[0].split("_")[-2]
        dates.append(fn)
        fn = fn + "_NDVI.tif"
        filenames.append(fn)        
    for i in range (len(Myfiles22)):
        os.chdir (dir_step2)
        in_raster = dir_step2 + "\\" + Myfiles22[i]
        NDVI_conversion(in_raster, temp, filenames[i])   
    CopyClearTemp(temp, dir_step2)
#---------------------------------------------
#    print '\nCorection for negative values... 
#[VALIDATE WATER PIXELS!!!!]'
    Myfiles23=SearchFolder(dir_step2, 'NDVI.tif')  
    for i in range (len(Myfiles23)):
        os.chdir (dir_step2)
        in_raster = dir_step2 + "\\" + Myfiles23[i]
        NDVI_correction(in_raster, temp, filenames[i])  
    CopyClearTemp(temp, dir_step2)   
#---------------------------------------------
#    print '\nResampling images to a higher resolution...'
    Myfiles24=SearchFolder(dir_step2, '.tif')     
    for i in range (len(Myfiles24)):
        os.chdir (dir_step2)
        in_raster = dir_step2 + "\\" + Myfiles24[i]
        out_raster = temp + '\\' + Myfiles24[i]
        CellSize = GetCellSize(in_raster)
        new_xres = CellSize[0]/2
        new_yres = CellSize[1]/2
        cmd= 'gdalwarp -q -multi -of GTiff -co TILED=YES -tr %s %s -overwrite %s %s' % (new_xres, new_yres, in_raster, out_raster)
        os.system (cmd)        
    CopyClearTemp(temp, dir_step2)   
#---------------------------------------------
    print '\nReprojecting and resampling NDVI maps ...'    
    Myfiles25=SearchFolder(dir_step2, '.tif')
    
    data_rast = gdal.Open(dir_input_raster)
    t_project = data_rast.GetProjection()
    t_transform = data_rast.GetGeoTransform()
    newt_xres = t_transform[1]
    newt_yres = t_transform[5]
    
    for i in range (len(Myfiles25)):
        os.chdir (dir_step2)
        raster_5 = gdal.Open(dir_step2 + '\\' + Myfiles25[i])
        project_5 = raster_5.GetProjection()
        transform_5 = raster_5.GetGeoTransform()
        in_raster = dir_step2 + "\\" + Myfiles25[i]
        out_raster = temp + '\\' + Myfiles25[i]  
        cmd= 'gdalwarp -q -multi -of GTiff -co TILED=YES -s_srs %s -t_srs %s -tr %s %s -r cubic -overwrite %s %s' % (project_5, t_project, newt_xres, newt_yres, in_raster, out_raster)
        os.system (cmd)    
    del data_rast
    del raster_5
    CopyClearTemp(temp, dir_step2)       
#---------------------------------------------
    print '\nAdjusting extend...'
    Myfiles26=SearchFolder(dir_step2, '.tif')
    for i in range (len(Myfiles26)):
        os.chdir (dir_step2)
        raster_6 = gdal.Open(dir_step2 + '\\' + Myfiles26[i])
        project_6 = raster_6.GetProjection()
        transform_6 = raster_6.GetGeoTransform()
        os.chdir (dir_step2)
        in_raster = dir_step2 + "\\" + Myfiles26[i]
        out_raster = temp + '\\' + Myfiles26[i]
    #finding the extent of ProbaV maps and raster
        Inp_CellSize = GetCellSize(in_raster)
        cellsize = Inp_CellSize[0]
        Inp_Extent = GetExtent(in_raster)
        xll_inp = Inp_Extent[0]
        yll_inp = Inp_Extent[1]
        Ext_Extent = GetExtent(dir_input_raster)
        xll_ext = Ext_Extent[0]
        yll_ext = Ext_Extent[1]
    #computing the shift in x (assuming that both rasters have the same cellsize!)
        x_shift = (xll_ext - xll_inp)/cellsize
        x_shift = x_shift - (round(x_shift) - 1)
        x_shift = cellsize-(cellsize*x_shift)    
    #computing the shift in y (assuming that both rasters have the same cellsize!)
        y_shift = (yll_ext - yll_inp)/cellsize
        y_shift = y_shift - (round(y_shift) - 1)
        y_shift = cellsize-(cellsize*y_shift)    
    #apllying shift to the map extent
        new_xll = xll_inp - x_shift
        new_yll = yll_inp - y_shift
        max_xll = Inp_Extent[2] - x_shift
        max_yll = Inp_Extent[3] - y_shift
        cmd= 'gdal_translate -a_ullr %s %s %s %s -stats %s %s' % (new_xll,max_yll,max_xll,new_yll, in_raster, out_raster)
        os.system (cmd)         
    print 'x shift: ' + str(x_shift) + ' [m]'
    print 'y shift: ' + str(y_shift) + ' [m]'    
    del raster_6
#    raster_6.close()
    CopyClearTemp(temp, dir_step2)
#---------------------------------------------
    print '\nClipping and generating NDVI.tif maps...'
    Myfiles27=SearchFolder(dir_step2, '.tif')
    #gdaltindex clipper.shp clipshapeRaster.tif
    cutline = temp + "\\cutline.shp"
    cmd = 'gdaltindex %s %s' % (cutline, dir_input_raster)
    os.system (cmd)         
    for i in range (len(Myfiles27)):
        raster_7 = gdal.Open(dir_step2 + '\\' + Myfiles27[i])
        project_7 = raster_7.GetProjection()
        transform_7 = raster_7.GetGeoTransform()
        in_raster = dir_step2 + "\\" + Myfiles27[i]
        out_raster = temp + "\\" + Myfiles27[i]
        cmd= 'gdalwarp -q -multi -of GTiff -co TILED=YES -cutline %s -crop_to_cutline %s %s' % (cutline, in_raster, out_raster)
        os.system (cmd)   
    del raster_7
#    raster_7.close()
    CopyClearTemp(temp, dir_step2)    
else:
    pass
#---------------------------------------------
# - - - STEP 3 - - - STEP 3 - - - STEP 3 - - -
#--------------------------------------------- 
if step3 == 1:
    print '\nGenerating LAI.tif maps...'    
    Myfiles3=SearchFolder(dir_step2, '.tif')
    
    for i in range (len(Myfiles3)):
        in_raster = dir_step2 + "\\" + Myfiles3[i]
        NDVI_source = gdal.Open(in_raster)
        band_info = NDVI_source.GetRasterBand(1)
        nodata = band_info.GetNoDataValue()
        xSize = band_info.XSize
        ySize = band_info.YSize
        LAI_Map_Tiff(in_raster,dir_step3,dates[i])        
        del NDVI_source
else:
    pass
#---------------------------------------------
# - - - STEP 4 - - - STEP 4 - - - STEP 4 - - -
#--------------------------------------------- 
if step4 == 1:
    print '\nGenerating LAI.asc maps...'
    Myfiles4=SearchFolder(dir_step3, '.tif')
    os.chdir(dir_step4)
    for i in range (len(Myfiles4)):
        in_raster = dir_step3 + "\\" + Myfiles4[i]
        out_raster = dir_step4 + "\\LAI_" + dates[i] + ".asc"
        if os.path.exists(out_raster):
            os.remove(out_raster)
        cmd= 'gdal_translate -q -of AAIGrid %s %s' % (in_raster, out_raster)    
        os.system (cmd)    
else:
    pass
#---------------------------------------------
# - - - STEP 5 - - - STEP 5 - - - STEP 5 - - -
#--------------------------------------------- 
if step5 == 1:
#    print '\n Step 5'
    print '\nGenerating monthly aggregated LAI.tif maps... '
    Myfiles5=SearchFolder(dir_step3, '.tif')        
    data_src = gdal.Open(dir_step3 + "\\" + Myfiles5[0])
    band_info = data_src.GetRasterBand(1)
    xarray = band_info.XSize
    yarray = band_info.YSize    
    filenames = []
    dates = []
    for i in range (len(Myfiles5)):
        breakList = Myfiles5[i].split("\\")
        fn = breakList [-1]
        fn = fn[:-4]
        filenames.append(fn)
        fn2 = fn.split("_")
        fn2 = fn2[-1]
        dates.append(fn2)
    years = []
    months = ['01', '02', '03', '04','05', '06','07', '08','09', '10','11', '12']
    for j in range (len(dates)):
        date = dates[j]
        year = date[:4]
        if year not in years: 
            years.append(year)
    in_raster = dir_step3
    out_raster = dir_step5    
    
    print '\nStatus report - number of available products for each month'
    for i in range(len(years)):
        for k in range(12):
            LAI_Map_Agg(in_raster, out_raster, filenames, months[k], years[i], xarray, yarray)            
else:
    pass
#---------------------------------------------
# - - - STEP 6 - - - STEP 6 - - - STEP 6 - - -
#--------------------------------------------- 
if step6 == 1:
#    print '\n Step 6'
    print '\nGenerating aggregated LAI.asc maps...'
    Myfiles6=SearchFolder(dir_step5, '.tif')    
    filenames = []
    dates = []
    for i in range (len(Myfiles6)):
        breakList = Myfiles6[i].split("\\")
        fn = breakList [-1]
        fn = fn[:-4]
        filenames.append(fn)
        fn2 = fn.split("_")
        fn2 = fn2[-1]
        dates.append(fn2)    
    for i in range (len(Myfiles6)):
        in_raster = dir_step5 + "\\" + Myfiles6[i]
        out_raster = dir_step6+ "\\" + dates[i] + ".asc"
        if os.path.exists(out_raster):
            os.remove(out_raster)
        cmd= 'gdal_translate -q -of AAIGrid %s %s' % (in_raster, out_raster)
        os.system (cmd)    
else:
    pass
#---------------------------------------------
# - - - STEP 7 - - - STEP 7 - - - STEP 7 - - -
#--------------------------------------------- 
if step7 == 1:   
#    print '\n Step 7'
    print '\nInterpolating and generating additonal monthly LAI.asc maps...'
    print 'WIP - work in progress'
else:
    pass
#---------------------------------------------

get_ipython().magic('reset -sf')
print '\n PROCESSING COMPLETE'
