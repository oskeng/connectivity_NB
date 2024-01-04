#!/usr/bin/python3.11
#
# Structural connectivity in Norrbotten county: forests
#
# Author: Oskar Englund
# Email: oskar.englund@miun.se
# Github: https://github.com/oskeng/konnektivitet_NB.git
#
######################

#from typing import Any
#import sys
import grass.script as gscript
#import time
from grass.pygrass.modules import Module
#from grass.pygrass.modules.shortcuts import general as g
#from grass.pygrass.modules.shortcuts import vector as v
#from grass.pygrass.modules.shortcuts import raster as r
#from colorama import Fore
from tkinter import *
from tkinter import filedialog as fd
#import tkinter.messagebox
import time
from datetime import datetime
#from subprocess import PIPE
#from grass.script import parser, parse_key_val
#import pandas as pd

#####################################################
# Note: Default values - study area can be set in GUI
#
region = ''
buffer = ''
focal_points_number = ''
cumcur = ''
output_suffix = ''

wetland_forest_res = ''
other_forest_res = ''
other_NV_res = ''
nonnat_veg_res = ''
no_veg_res = ''

wetland_forest_res_def = '15'
other_NV_res_def = '20'
other_forest_res_def = '50'
nonnat_veg_res_def = '150'
no_veg_res_def = '300'


#####################################################



#####################################################
# Variables

# necessary input data to be placed in the active mapset
nmd_gen_sv = 'nmd_gen_sv_updated@update_NMD'  # NMD updated with recent fellings and transmission lines (update_NMD.py)
input_HCV_kskog = 'out_input_HCV_kskog_final@HCV_kskog'  # location of protected, restricted and continuity forest
input_density_HCV = 'result_density_forest_HCV_kskog_NB_250m_v2@density_analysis'  # copied from density_analysis_output
study_area_raw = ''  # should be named "input_study_area_raw_' + region + ".  Region is selected in the GUI. For county level: NB

# datasets created in datasets()
nmd_gen = ''
nmd_gen_20m = ''
nmd_gen_nobuffer = ''
HCV_kskog = ''
density_HCV = ''
study_area = ''
wetland_forest = ''
other_forest = ''
other_NV = ''
nonnat_veg = ''
no_veg = ''

HCV_density_res = ''
wetland_forest_res_ras = ''
other_NV_res_ras = ''
other_forest_res_ras = ''
nonnat_veg_res_ras = ''
no_veg_res_ras = ''

# datasets created in focal_points()
focal_points_ras = ''
focal_points_ras_20m =''
focal_points_vect = ''

# datasets created in structural_resistance()
resistance = ''
resistance_20m = ''

# paths
export_raster_path = ''
export_vector_path = ''
circuitscape_path = ''

# Here, variables are set based on the region selected in GUI
def setvariables(region):

        miniMessage(region)

        suffix = str(output_suffix)

        # datasets()
        global nmd_gen
        nmd_gen = region + '_calc_nmd_gen'
        global nmd_gen_20m
        nmd_gen_20m = region + '_calc_nmd_gen_20m'
        global nmd_gen_nobuffer
        nmd_gen_nobuffer = region + '_calc_nmd_gen_nobuffer'
        global study_area_raw
        study_area_raw = 'input_study_area_raw_' + region
        global study_area
        study_area = region + '_study_area' # Study area with specified buffer
        global HCV_kskog
        HCV_kskog = region + '_HCV_kskog'
        global wetland_forest
        wetland_forest = region + '_wetland_forest'
        global other_forest
        other_forest = region + '_other_forest'
        global other_NV
        other_NV = region + '_other_NV'
        global nonnat_veg
        nonnat_veg = region + '_nonnat_veg'
        global no_veg
        no_veg = region + '_no_veg'
        global density_HCV
        density_HCV = region + '_density_HCV'
        global HCV_density_res
        HCV_density_res = region + '_HCV_density_res'
        global wetland_forest_res_ras
        wetland_forest_res_ras = region + '_wetland_forest_res_ras'
        global other_NV_res_ras
        other_NV_res_ras = region + '_other_NV_res_ras'
        global other_forest_res_ras
        other_forest_res_ras = region + '_other_forest_res_ras'
        global nonnat_veg_res_ras
        nonnat_veg_res_ras = region + '_nonnat_veg_res_ras'
        global no_veg_res_ras
        no_veg_res_ras = region + '_no_veg_res_ras'

        # focal_points()
        global focal_points_ras
        focal_points_ras = 'out_' + region + '_calc_focal_points_ras_' + suffix
        global focal_points_ras_20m
        focal_points_ras_20m = 'out_' + region + '_calc_focal_points_ras_20m_' + suffix
        global focal_points_vect
        focal_points_vect = 'out_' + region + '_calc_focal_points_' + suffix

        #structural_resistance()
        global resistance
        resistance = 'out_' + region + '_calc_resistance_' + suffix
        global resistance_20m
        resistance_20m = 'out_' + region + '_calc_resistance_20m_' + suffix

        #paths
        global export_raster_path
        export_raster_path = "/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Analys/Output/Forest/new/" + region + "/grassout_ras/"
        global export_vector_path
        export_vector_path = "/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Analys/Output/Forest/new/" + region + "/grassout_vect/"
        global circuitscape_path
        circuitscape_path = "/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Analys/Omniscape/Forest/new/" + region + '/'

################################################
#
# General functions
#
################################################

def get_time():
    now = datetime.now()
    return now.strftime("%H:%M:%S")


def majorMessage(message):
    # print(Fore.BLUE + "\n######################################################\n")
    # print(message)
    # print("\n######################################################\n" + Fore.RESET)

    Module("g.message", message="\n \n" + message + "\n \n", flags="w")

def minorMessage(message):
    # print(Fore.BLUE + "\n#######################\n")
    # print(message)
    # print("\n#######################\n" + Fore.RESET)

    Module("g.message", message="\n \n" + message + "\n \n")

def miniMessage(message):
    # gscript.core.info("\n\n---> " + message + "\n\n")
    # print(Fore.BLUE + "\n")
    # print(message)
    # print(Fore.RESET)

    Module("g.message", message="\n \n" + message + "\n \n")


################################################
#
# Model functions
#
################################################

# This function creates input data based on existing national datasets and the specified study region.
# Only needs to be run once for each region

def datasets():
    ###
    majorMessage("PREPARING DATASETS...")
    ###

    Module("g.region", vector=study_area_raw, res=10, align=nmd_gen_sv, zoom=nmd_gen_sv)

    ###
    minorMessage("...creating buffered study area if set to > 0...")
    ###

    Module("v.buffer", input=study_area_raw, output=study_area, type="area", distance=buffer, overwrite=True)

    ###
    minorMessage("...creating input data clipped to study area...")
    ###

    Module("g.region", vector=study_area, res=10, align=nmd_gen_sv, zoom=nmd_gen_sv)

    Module("r.mask", vector=study_area)

    ###
    miniMessage("...Creating " + nmd_gen + "...")
    ###

    Module("r.mapcalc",
           expression=nmd_gen + " = " + nmd_gen_sv, overwrite=True)

    ###
    miniMessage("...Creating " + HCV_kskog + "...")
    ###

    Module("r.mapcalc",
           expression=HCV_kskog + " = " + input_HCV_kskog, overwrite=True)

    Module("r.null", map=HCV_kskog, null=0)

    ###
    miniMessage("...Creating " + other_forest + "...")
    ###

    Module("r.mapcalc",
           expression=other_forest + "= if( " + nmd_gen + " != 118 & " + nmd_gen + " != 128 & " + nmd_gen + " != 130 & " + nmd_gen + " > 110 & " + input_HCV_kskog + " == 0, 1, 0)",
           overwrite=True)

    ###
    miniMessage("...Creating " + other_NV + "...")
    ###

    Module("r.mapcalc", expression=other_NV + " = if(( " + nmd_gen + "== 2 | " + nmd_gen + " == 42), 1)", overwrite=True)

    ###
    miniMessage("...Creating " + nonnat_veg + "...")
    ###

    Module("r.mapcalc", expression=nonnat_veg + " = if( " + nmd_gen + " == 3 | " + nmd_gen + "== 54 | " + nmd_gen + "== 118 | " + nmd_gen + " == 128 | " + nmd_gen + "== 130, 1)", overwrite=True)

    ###
    miniMessage("...Creating " + no_veg + "...")
    ###

    Module("r.mapcalc", expression=no_veg + " = if( " + nmd_gen + "== 41 | " + nmd_gen + " == 51 | " + nmd_gen + " == 52 | " + nmd_gen + " == 53 | " + nmd_gen + "== 61 | " + nmd_gen + " == 62, 1)", overwrite=True)

    ###
    miniMessage("...Creating " + wetland_forest + "...")
    ###
    #Module("r.mapcalc", expression=wetland_forest + " = if( " + nmd_gen + " == 121 |  " + nmd_gen + " == 122 | " + nmd_gen + " == 123 | " + nmd_gen + "== 124 | " + nmd_gen + " == 125 | " + nmd_gen + "== 126 | " + nmd_gen + " == 127, 1)", overwrite=True)

    Module("r.mapcalc",
           expression=wetland_forest + " = if( " + nmd_gen + " > 120 & " + nmd_gen + " < 128, 1)", overwrite=True)

    ###
    miniMessage("...Creating " + density_HCV + "...")
    ###

    Module("r.mapcalc",
           expression=density_HCV + " = " + input_density_HCV, overwrite=True)

    Module("r.null", map=input_density_HCV, null=0)

    Module("r.mask", flags="r")

    ###
    minorMessage("...creating input data clipped to study area... ---> DONE")
    ###

    ###
    minorMessage("...creating nmd without buffer: " + nmd_gen_nobuffer + "...")
    ###

    Module("r.mask", vector=study_area_raw)

    Module("r.mapcalc",
           expression=nmd_gen_nobuffer + " = " + nmd_gen, overwrite=True)

    Module("r.null",
           map=nmd_gen_nobuffer,
           setnull=0)

    Module("r.mask", flags="r")


    ###
    minorMessage("...Creating nmd_gen with 20 m resolution: " + nmd_gen_20m + "...")
    ###

    Module("r.mask", vector=study_area)

    Module("g.region", raster=nmd_gen, res=20)

    Module("r.resample", input=nmd_gen, output=nmd_gen_20m, overwrite=True)

    Module("r.mask", flags="r")

    ###
    majorMessage("...DATASETS PREPARED")
    ###


def focal_points():
    majorMessage("CREATING FOCAL POINTS...")

    create_focal_points()
    save_focal_points()

    majorMessage("...DONE, FOCAL POINTS CREATED")


def create_focal_points():
    start_time = time.time()
    Module("g.region", raster=nmd_gen)


    # Mask cells with lowest resistance and randomly create points

    Module("r.mask", raster=nmd_gen_nobuffer, flags="i")

    Module("r.mapcalc",
           expression="temp_resistance" + " = " + resistance, overwrite=True)

    Module("r.mask", flags="r")

    Module("r.mask", raster="temp_resistance", maskcats="1 thru 11")

    Module("r.random.cells",
            output="temp_random_cells",
            distance="2500",
            ncells=focal_points_number,
            seed="1234",  # If omitted, output will differ every time. If set, output will always be the same,
            overwrite=True)

    Module("r.mapcalc",
           expression=focal_points_ras + " = if(temp_random_cells > 1,1)", overwrite=True)

    Module("r.to.vect",
           input=focal_points_ras,
           output=focal_points_vect,
           type="point",
           overwrite=True)

    Module("r.mask", flags="r")

    miniMessage(" ...and also with 20m resolution...")

    Module("g.region", raster=nmd_gen_20m)
    Module("r.resamp.stats", input=focal_points_ras, output=focal_points_ras_20m, method="maximum", overwrite=True)

def save_focal_points():
    Module("g.region", raster=nmd_gen_nobuffer)

    minorMessage("...saving focal points to shapefile...")

    Module("v.out.ogr",
           flags='s',
           overwrite=True,
           input=focal_points_vect,
           output=export_vector_path + focal_points_vect,
           format="ESRI_Shapefile")

    minorMessage("...saving focal points to ascii...")

    Module("r.out.gdal",
           flags="mf",
           input=focal_points_ras,
           output= circuitscape_path + focal_points_ras + ".asc",
           format="AAIGrid",
           type="Int16",
           createopt="FORCE_CELLSIZE=TRUE",
           nodata=-9999,
           overwrite=True,
           quiet=True)

    Module("g.region", raster=nmd_gen_20m)
    Module("r.out.gdal",
           flags="mf",
           input=focal_points_ras_20m,
           output= circuitscape_path + focal_points_ras_20m + ".asc",
           format="AAIGrid",
           type="Int16",
           createopt="FORCE_CELLSIZE=TRUE",
           nodata=-9999,
           overwrite=True,
           quiet=True)

def calc_resistance():
    majorMessage("CREATING RESISTANCE LAYER...")

    structural_resistance()
    save_resistance()

    majorMessage("...RESISTANCE LAYER CREATED")


def structural_resistance():
    #    Module("r.mask", flags="r")

    Module("g.region", raster=nmd_gen, align=nmd_gen)

    ###
    minorMessage(" ...creating resistance input maps...")
    ###

    Module("r.mapcalc",
           expression=HCV_density_res + ' = if(' + HCV_kskog + ' > 0, int((100 - float(' + density_HCV + ')) / 10 + 1.99), \
           if(isnull(' + HCV_kskog + '),9999,9999))', overwrite=True)

    Module("r.mapcalc",
           expression=wetland_forest_res_ras + '= if(' + wetland_forest + '> 0, ' + wetland_forest_res + ', 9999)', overwrite=True)

    Module("r.mapcalc",
           expression=other_NV_res_ras + '= if(' + other_NV + '> 0, ' + other_NV_res + ', 9999)', overwrite=True)

    Module("r.mapcalc",
           expression=other_forest_res_ras + '= if(' + other_forest + '> 0, ' + other_forest_res + ', 9999)', overwrite=True)

    Module("r.mapcalc",
           expression=nonnat_veg_res_ras + '= if(' + nonnat_veg + '> 0 | ' + nmd_gen + ' == 54,' + nonnat_veg_res + ', 9999)', overwrite=True)

    Module("r.mapcalc",
           expression=no_veg_res_ras + '= if(' + no_veg + '> 0, ' + no_veg_res + ', 9999)', overwrite=True)
    ###
    minorMessage(" ...combining input resistance maps...")
    ###

    # First patch NV+forests by minimum resistance

    Module("r.series",
           input=HCV_density_res + ',' + wetland_forest_res_ras + ',' + other_NV_res_ras + ',' +
                 other_forest_res_ras,
           output="temp_resistance", method='minimum', overwrite=True)

    # Then patch the above with nonnat_veg and no_veg by maximum resistance, to avoid that misclassification creates low res where there is nonnat veg/noveg

    Module("r.mapcalc",
           expression=resistance + "= if(" + no_veg_res_ras + "<9999," + no_veg_res_ras + ",if(" + nonnat_veg_res_ras + "<9999," + nonnat_veg_res_ras + ",temp_resistance))", overwrite=True)

    Module("r.null",
           map=resistance,
           setnull=9999)

    Module("g.region", raster=nmd_gen_20m)

    Module("r.mapcalc", expression=resistance_20m + '=' + resistance, overwrite=True)

    Module("g.region", raster=nmd_gen, align=nmd_gen)

def save_resistance():

    Module("g.region", raster=nmd_gen)

    minorMessage(" ...saving resistance layer as geotiff and ascii...")

    Module("r.out.gdal",
           input=resistance,
           output=export_raster_path + resistance + ".tif",
           type="Float64",
           overwrite=True,
           quiet=True)

    Module("r.out.gdal",
           flags="mf",
           input=resistance,
           output= circuitscape_path + resistance + ".asc",
           format="AAIGrid",
           type="Int16",
           createopt="FORCE_CELLSIZE=TRUE",
           nodata=-9999,
           overwrite=True,
           quiet=True)

    Module("g.region", raster=nmd_gen_20m)

    Module("r.out.gdal",
           input=resistance_20m,
           output=export_raster_path + resistance_20m + ".tif",
           type="Float64",
           overwrite=True,
           quiet=True)

    Module("r.out.gdal",
           flags="mf",
           input=resistance_20m,
           output= circuitscape_path + resistance_20m + ".asc",
           format="AAIGrid",
           type="Int16",
           createopt="FORCE_CELLSIZE=TRUE",
           nodata=-9999,
           overwrite=True,
           quiet=True)

def post_processing():

    majorMessage("STARTING POST-PROCESSING...")

    global cumcur

    cumcur_import = "omni_norm_cumcur_" + region + "_" + output_suffix
    cumcur_import_resamp = cumcur_import + "_resamp"
    cumcur_import_resamp_clip = cumcur_import_resamp + "_clip"
    cumcur_import_resamp_class = cumcur_import_resamp_clip + "_class"

    Module("g.region", vector=study_area, res=10, align=nmd_gen)

    Module("r.mask", raster=nmd_gen, maskcats="62", flags="i")

    minorMessage("importing and resampling")

    # Module("r.import", input=cumcur, output=cumcur_import, overwrite=True, resample="lanczos_f", resolution="value", resolution_value= 10, memory="20000")

    Module("r.import", input=cumcur, output=cumcur_import, overwrite=True, flags="o")

    minorMessage("importing and resampling")

    Module("r.resamp.interp", overwrite=True, input=cumcur_import, output=cumcur_import_resamp, method="lanczos")

    minorMessage("importing and resampling")

    # Clip to study area

    Module("g.region", vector=study_area_raw, res=10, align=nmd_gen)

    Module("r.mask", flags="r")

    Module("r.mask", vector=study_area_raw)

    Module("r.mapcalc", expression=cumcur_import_resamp_clip + "=" + cumcur_import_resamp, overwrite=True)

    # majorMessage("temporary fix for wetland data - remember to comment out")
    #
    # Module("r.mapcalc", expression='temp_cumcur_import_resamp_clip = if( ' + nmd_gen + '== 62, 0, ' + cumcur_import_resamp_clip + ')', overwrite=True)
    #
    # cumcur_import_resamp_clip = 'temp_cumcur_import_resamp_clip'
    #
    # majorMessage("temporary fix completed")

    Module("r.null",
           map=cumcur_import_resamp_clip,
           setnull=0)

    # Classify using quantiles

    post_processing_path = "/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Analys/Omniscape/Forest/new/" + region + "/post_processing/"

    Module("r.quantile",
            flags="r",
            overwrite=True,
            input=cumcur_import_resamp_clip,
            quantiles=10,
            file=post_processing_path + 'quantiles.txt',
            )

    Module("r.recode",
           input=cumcur_import_resamp_clip,
           output=cumcur_import_resamp_class,
           rules=post_processing_path + 'quantiles.txt',
           overwrite=True,
           )

    Module("r.out.gdal",
           input=cumcur_import_resamp_class,
           output=post_processing_path + 'classified_norm_cumcur_' + region + "_" + output_suffix + ".tif",
           type="Int32",
           overwrite=True,
           quiet=True)

    Module("r.mask", flags="r")

    majorMessage("...POST-PROCESSING COMPLETED")


def generate_init():
    Module("g.region", raster=nmd_gen, align=nmd_gen)
    gscript.core.info("\n ---> Nope, not yet...\n \n")
    return


def init_circuitscape():
    Module("g.region", raster=nmd_gen, align=nmd_gen)
    gscript.core.info("\n ---> Nope, not yet...\n \n")


##################################################################
#
#                            GUI
#
##################################################################

# class MainApplication(Frame):
#     def __init__(self, parent, *args, **kwargs):
#         Frame.__init__(self, parent, *args, **kwargs)
#         self.parent = parent
#
#     """
#     def counter():
#         elapsed_time = int(time.time() - start_time)
#         return str(elapsed_time)
#     """

a = Tk()
a.geometry("800x800")

# root.withdraw() # THIS HIDE THE WINDOW

CheckVar1 = IntVar()
CheckVar2 = IntVar()
CheckVar3 = IntVar()
CheckVar4 = IntVar()
CheckVar5 = IntVar()
CheckVar6 = IntVar()
CheckVar7 = IntVar()
CheckVar8 = IntVar()
CheckVar9 = IntVar()
CheckVar10 = IntVar()
CheckVar11 = IntVar()
CheckVar12 = IntVar()

notcompleted = "Not completed"
running = "Running..."
completed = "--------> Completed: "
input_region_label = Label(a, text="Input region here: (Default: NB)\n\n Restart script when changing region\n")
region_status_label = Label(a, text="Current region: " + region)
region_info_label = Label(a, text="NB (entire county) \n RA: (Råneälven) \n test_sundom\n test_gallivare\n test_granlandet\n ")

input_buffer_label = Label(a, text="\nSpecify buffer size in meter (Default: 10,000)\n")
buffer_status_label = Label(a, text="Current buffer: " + str(buffer))

input_suffix_label = Label(a, text="\nSpecify suffix for output\n")
suffix_status_label = Label(a, text="Current suffix: " + str(output_suffix))

input_max_points_label = Label(a, text="\nSpecify max number of focal points (Default: 500)\n")
max_points_status_label = Label(a, text="Current max number of focal points: " + str(focal_points_number))
Title_label = Label(a, text="\n\nSelect operation", font=("Courier", 20))
Study_area_label = Label(a, text="\n_______________________________\nDefine study area\n", font=("Courier", 12))
Preparation_label = Label(a, text="\n_______________________________\nPrepare data\n", font=("Courier", 12))
Compute_label = Label(a, text="\n_______________________________\nGenerate Circuitscape input\n", font=("Courier", 12))
Circuitscape_label = Label(a, text="\n_______________________________\nCircuitscape\n", font=("Courier", 12))

resistance_label = Label(a, text="Resistance values")
label_wetland_forest_res = Label(a, text="Forest on wetland:")
label_other_forest_res = Label(a, text="Other forest:")
label_other_NV_res = Label(a, text="Other natural vegetation:")
label_nonnat_veg_res = Label(a, text="Non-natural vegetation:")
label_no_veg_res = Label(a, text="No vegetation:")

Post_processing_label = Label(a, text="\n_______________________________\nPost processing\n", font=("Courier", 12))
System_label = Label(a, text="\n_______________________________\nSystem\n", font=("Courier", 12))
prepare_datasets_label = Label(a, text=notcompleted)
generate_focal_points_label = Label(a, text=notcompleted)
compute_resistance_label = Label(a, text=notcompleted)
generate_init_file_label = Label(a, text=notcompleted)
init_circuitscape_label = Label(a, text=notcompleted)


# label.config(font=("Courier", 44))

###############
#
# GUI functions
#
###############

def retrieve_region():
    global region
    region = textbox_region.get("1.0", 'end-1c')

    if region == '':
        region = 'NB'

    region_status_label.config(text="Current region: " + region + " (" + get_time() + ")")
    region_status_label.update_idletasks()

    setvariables(region)

def retrieve_buffer():
    global buffer
    buffer = textbox_buffer.get("1.0", 'end-1c')

    if buffer == '':
        buffer = '10000'

    buffer_status_label.config(text="Current buffer: " + str(buffer) + " m (" + get_time() + ")")
    buffer_status_label.update_idletasks()

def retrieve_suffix():
    global output_suffix
    output_suffix = textbox_suffix.get("1.0", 'end-1c')

    suffix_status_label.config(text="Current suffix: " + str(output_suffix) + ' ' + get_time() + ")")
    suffix_status_label.update_idletasks()

def retrieve_max_points():
    global focal_points_number
    focal_points_number = textbox_max_points.get("1.0", 'end-1c')

    if focal_points_number == '':
        focal_points_number = '500'

    max_points_status_label.config(text="Max number of focal points: " + str(focal_points_number) + " (" + get_time() + ")")
    max_points_status_label.update_idletasks()

def prepare_datasets():
    prepare_datasets_label.config(text=running)
    prepare_datasets_label.update_idletasks()

    datasets()

    prepare_datasets_label.config(text=completed + get_time())
    prepare_datasets_label.update_idletasks()


def generate_focal_points():
    generate_focal_points_label.config(text=running)
    generate_focal_points_label.update_idletasks()

    focal_points()

    generate_focal_points_label.config(text=completed + get_time())
    generate_focal_points_label.update_idletasks()


def compute_resistance():

    global wetland_forest_res
    global other_forest_res
    global other_NV_res
    global nonnat_veg_res
    global no_veg_res

    #HCV_res = textbox_HCV_res.get("1.0", 'end-1c')
    wetland_forest_res = textbox_wetland_forest_res.get("1.0", 'end-1c')
    other_forest_res = textbox_other_forest_res.get("1.0", 'end-1c')
    other_NV_res = textbox_other_NV_res.get("1.0", 'end-1c')
    nonnat_veg_res = textbox_nonnat_veg_res.get("1.0", 'end-1c')
    no_veg_res = textbox_no_veg_res.get("1.0", 'end-1c')

    # Default resistance values

    if wetland_forest_res == '':
        wetland_forest_res = wetland_forest_res_def

    if other_NV_res == '':
        other_NV_res = other_NV_res_def

    if other_forest_res == '':
        other_forest_res = other_forest_res_def

    if nonnat_veg_res == '':
        nonnat_veg_res = nonnat_veg_res_def

    if no_veg_res == '':
        no_veg_res = no_veg_res_def

    compute_resistance_label.config(text=running)
    compute_resistance_label.update_idletasks()

    calc_resistance()

    compute_resistance_label.config(text=completed + get_time())
    compute_resistance_label.update_idletasks()


def generate_init_file():
    generate_init_file_label.config(text=running)
    generate_init_file_label.update_idletasks()

    generate_init()

    generate_init_file_label.config(text=completed + get_time())
    generate_init_file_label.update_idletasks()


def initiate_circuitscape():
    init_circuitscape_label.config(text=running)
    init_circuitscape_label.update_idletasks()

    init_circuitscape()

    init_circuitscape_label.config(text=completed + get_time())
    init_circuitscape_label.update_idletasks()


def start_post_processing():
    global cumcur
    cumcur = fd.askopenfilename()
    post_processing()


def reset_fields():
    labels = [prepare_datasets_label, generate_focal_points_label, compute_resistance_label, generate_init_file_label,
              init_circuitscape_label]

    for label in labels:
        label.config(text="Not completed")
        label.update_idletasks()


textbox_region = Text(a, height=1, width=10)
textbox_buffer = Text(a, height=1, width=10)
textbox_suffix = Text(a, height=1, width=10)
textbox_max_points = Text(a, height=1, width=10)
textbox_wetland_forest_res = Text(a, height=1, width=10)
textbox_other_forest_res = Text(a, height=1, width=10)
textbox_other_NV_res = Text(a, height=1, width=10)
textbox_nonnat_veg_res = Text(a, height=1, width=10)
textbox_no_veg_res = Text(a, height=1, width=10)

# command=lambda: retrieve_input() >>> just means do this when i press the button

save_region_button = Button(a, text="Save", activebackground="black",
                            activeforeground="WHITE", \
                            bg="green", height=1, width=10, command=lambda: retrieve_region())

save_buffer_button = Button(a, text="Save", activebackground="black",
                            activeforeground="WHITE", \
                            bg="green", height=1, width=10, command=lambda: retrieve_buffer())

save_suffix_button = Button(a, text="Save", activebackground="black",
                            activeforeground="WHITE", \
                            bg="green", height=1, width=10, command=lambda: retrieve_suffix())

save_max_points = Button(a, text="Save", activebackground="black",
                            activeforeground="WHITE", \
                            bg="green", height=1, width=10, command=lambda: retrieve_max_points())

prepare_datasets_button = Checkbutton(a, text="Prepare datasets", activebackground="black",
                                      activeforeground="WHITE", \
                                      bg="green", width=35, bd=10, variable=CheckVar1, onvalue=1, offvalue=0, \
                                      command=prepare_datasets)

generate_focal_points_button = Checkbutton(a, text="Generate focal points", activebackground="black",
                                           activeforeground="WHITE", \
                                           bg="green", width=35, bd=10, variable=CheckVar2, onvalue=1, offvalue=0, \
                                           command=generate_focal_points)

compute_resistance_button = Checkbutton(a, text="Compute resistance layer", activebackground="black",
                                        activeforeground="WHITE", \
                                        bg="green", width=35, bd=10, variable=CheckVar3, onvalue=1, offvalue=0, \
                                        command=compute_resistance)

post_processing_button = Checkbutton(a, text="Run post processing", activebackground="black",
                                       activeforeground="WHITE", \
                                       bg="green", width=35, bd=10, variable=CheckVar6, onvalue=1, offvalue=0, \
                                       command=start_post_processing)

reset_button = Checkbutton(a, text="Reset fields", activebackground="black", activeforeground="WHITE", \
                           bg="orange", width=35, bd=10, fg="black", variable=CheckVar12, onvalue=1, offvalue=0, \
                           command=reset_fields)

quit_button = Checkbutton(a, text="Quit", activebackground="black", activeforeground="WHITE", \
                          bg="red", width=35, bd=10, fg="black", variable=CheckVar12, onvalue=1, offvalue=0, \
                          command=a.destroy)


Title_label.grid(row=0, column=0)
Study_area_label.grid(row=2, column=0)

input_region_label.grid(row=3, column=0)
textbox_region.grid(row=4, column=0)
region_status_label.grid(row=4, column=1)
region_info_label.grid(row=4, column=2)
save_region_button.grid(row=5, column=0)

input_buffer_label.grid(row=6, column=0)
textbox_buffer.grid(row=7, column=0)
buffer_status_label.grid(row=7, column=1)
save_buffer_button.grid(row=8, column=0)

input_suffix_label.grid(row=9, column=0)
textbox_suffix.grid(row=10, column=0)
suffix_status_label.grid(row=10, column=1)
save_suffix_button.grid(row=11, column=0)

Preparation_label.grid(row=12, column=0)
prepare_datasets_button.grid(row=13, column=0)
prepare_datasets_label.grid(row=13, column=1)

Compute_label.grid(row=14, column=0)
resistance_label.grid(row=15, column=1)

label_wetland_forest_res.grid(row=16, column=0)
textbox_wetland_forest_res.grid(row=16, column=1)

label_other_NV_res.grid(row=17, column=0)
textbox_other_NV_res.grid(row=17, column=1)

label_other_forest_res.grid(row=18, column=0)
textbox_other_forest_res.grid(row=18, column=1)

label_nonnat_veg_res.grid(row=19, column=0)
textbox_nonnat_veg_res.grid(row=19, column=1)

label_no_veg_res.grid(row=20, column=0)
textbox_no_veg_res.grid(row=20, column=1)

compute_resistance_button.grid(row=21, column=0)
compute_resistance_label.grid(row=21, column=1)

# input_max_points_label.grid(row=22, column=0)
# textbox_max_points.grid(row=23, column=0)
# max_points_status_label.grid(row=23, column=1)
# save_max_points.grid(row=24, column=0)

# generate_focal_points_button.grid(row=25, column=0)
# generate_focal_points_label.grid(row=25, column=1)

# Circuitscape_label.grid(row=18, column=0)
# generate_init_file_button.grid(row=19, column=0)
# generate_init_file_label.grid(row=19, column=1)
# init_circuitscape_button.grid(row=20, column=0)
# init_circuitscape_label.grid(row=20, column=1)

Post_processing_label.grid(row=27, column=0)
post_processing_button.grid(row=27, column=0)

System_label.grid(row=28, column=0)
reset_button.grid(row=29, column=0)
quit_button.grid(row=30, column=0)

a.mainloop()

if __name__ == "__main__":
    print("test")
