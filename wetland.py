#!/usr/bin/python3.10
#
# Structural connectivity in Norrbotten county: wetlands
#
# Author: Oskar Englund
# Email: oskar.englund@miun.se
# Github: https://github.com/oskeng/konnektivitet_NB.git
#
######################
from typing import Any

import sys
import grass.script as gscript
import time
from grass.pygrass.modules import Module
from grass.pygrass.modules.shortcuts import general as g
from grass.pygrass.modules.shortcuts import vector as v
from grass.pygrass.modules.shortcuts import raster as r
from colorama import Fore
from tkinter import *
import tkinter.messagebox
import time
from datetime import datetime
from subprocess import PIPE
from grass.script import parser, parse_key_val
import pandas as pd

#####################################################
# Note: Default values - study area can be set in GUI
#
region = ''
buffer = ''

#####################################################



#####################################################
# Variables

# imported
nmd_gen_sv = 'input_nmd_gen_sv'
VMI_raw = 'input_wetlands'
# wetness_raw = 'input_wetness_slu'
wetness_raw = 'input_wetness_nmd'
fellings = 'input_recent_fellings'
improductive_forest = 'input_productivity'
protected_land = 'input_protected_land'


# datasets created in datasets()
nmd_gen_nobuffer = ''
nmd_gen = ''
nmd_gen_20m = ''
wetness = ''
wetness_20m = ''
VMI_study_area = ''
VMI = ''
VMI_wetlands = ''
study_area_raw = ''
study_area = ''
forest_mod = ''
nmd_gen_mod = ''
infrastructure = ''
infrastructure_20m = ''

# datasets created in focal_points()
optimal_wetness = ''
focal_points_ras = ''
focal_points_ras_20m =''
focal_points_vect = ''

# datasets created in create_focal_points_rasters()
# out_VMI_selected = 'out_VMI_selected_' + region
# out_VMI_selected_ras = 'out_VMI_selected_ras_' + region
# out_VMI_selected_ras_20m = 'out_VMI_selected_ras_20m_' + region

# datasets created in structural_resistance()
structural_res = ''
structural_res_corr = ''

# datasets created in ecosystem_modification()
ecosystem_modification_res = ''

# datasets created in combine_resistance()
structural_res_comb = ''
structural_res_comb_20m = ''
resistance = ''
resistance_20m = ''

# paths
export_raster_path = ''
export_vector_path = ''
ecosystem_modification_input = ''
circuitscape_path = ''
# Here, variables are set based on the region selected in GUI
def setvariables(region):

        miniMessage(region)

        # datasets()
        global nmd_gen_nobuffer
        nmd_gen_nobuffer = 'calc_nmd_gen_nobuffer_' + region
        global nmd_gen
        nmd_gen = 'calc_nmd_gen_' + region
        global nmd_gen_20m
        nmd_gen_20m = 'calc_nmd_gen_20m_' + region
        global wetness
        wetness = 'calc_wetness_' + region
        global wetness_20m
        wetness_20m = 'calc_wetness_20m_' + region
        global VMI_study_area
        VMI_study_area = 'calc_VMI_' + region
        global VMI
        VMI = 'calc_VMI_selected_' + region
        global VMI_wetlands
        VMI_wetlands = 'calc_wetlands_VMI_' + region
        global study_area_raw
        study_area_raw = 'input_study_area_raw_' + region
        global study_area
        study_area = 'calc_study_area_' + region  # Study area with specified buffer
        global forest_mod
        forest_mod = 'calc_forest_mod_' + region
        global nmd_gen_mod
        nmd_gen_mod = nmd_gen + '_mod'
        global infrastructure
        infrastructure = 'calc_infrastructure_' + region
        global infrastructure_20m
        infrastructure_20m = infrastructure + '_20m'

        # focal_points()
        global optimal_wetness
        optimal_wetness = 'calc_optimal_wetness_' + region
        global focal_points_ras
        focal_points_ras = "calc_focal_points_ras_" + region
        global focal_points_ras_20m
        focal_points_ras_20m = "calc_focal_points_ras_" + region + '_20m'
        global focal_points_vect
        focal_points_vect = "calc_focal_points_" + region

        #create_focal_points_rasters()
        global out_VMI_selected
        out_VMI_selected = 'out_VMI_selected_' + region
        global out_VMI_selected_ras
        out_VMI_selected_ras = 'out_VMI_selected_ras_' + region
        global out_VMI_selected_ras_20m
        out_VMI_selected_ras_20m = 'out_VMI_selected_ras_20m_' + region

        #structural_resistance()
        global structural_res
        structural_res = 'calc_structural_resistance_wetland_' + region
        global structural_res_corr
        structural_res_corr = structural_res + '_corr'

        #ecosystem_modification()
        global ecosystem_modification_res
        ecosystem_modification_res = 'calc_ecosystem_modification_' + region

        #combine_resistance()
        global structural_res_comb
        structural_res_comb = structural_res + "_comb"
        global structural_res_comb_20m
        structural_res_comb_20m = structural_res_comb + '_20m'
        global resistance
        resistance = 'calc_resistance_' + region
        global resistance_20m
        resistance_20m = 'calc_resistance_' + region + '_20m'
        global export_raster_path
        export_raster_path = "/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Analys/Output/Wetland/" + region + "/grassout_ras/"
        global export_vector_path
        export_vector_path = "/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Analys/Output/Wetland/" + region + "/grassout_vect/"
        global ecosystem_modification_input
        ecosystem_modification_input = "/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Analys/Input/ecosystem_modification"
        global circuitscape_path
        circuitscape_path = "/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Analys/Circuitscape/Input/" + region + '/'


# export paths

# export_gpkg_path = "/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Analys/Output/Wetland/" + region + "/grassout.gpkg"
# export_circuitscape_path = "/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Analys/Output/Wetland/circuitscape/" + region + "/"
# export_csv_path = "/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Analys/Output/csv/Wetland/" + region + "/"


# def main():
#     print("Model initiated................ \n Current time:", get_time(), "\n")
#
#     # print(Fore.WHITE)
#
#
# # Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     main()

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
    minorMessage("...creating buffer if set to > 0...")
    ###

    Module("v.buffer", input=study_area_raw, output=study_area, type="area", distance=buffer, overwrite=True)

    ###
    minorMessage("...clipping rasters to study area...")
    ###

    Module("g.region", vector=study_area, res=10, align=nmd_gen_sv, zoom=nmd_gen_sv)

    # Module("r.mask", flags="r")

    Module("r.mask", vector=study_area_raw)

    Module("r.mapcalc",
           expression=nmd_gen_nobuffer + " = " + nmd_gen_sv, overwrite=True)

    Module("r.mask", flags="r")

    Module("r.mask", vector=study_area)

    Module("r.mapcalc",
           expression=nmd_gen + " = " + nmd_gen_sv, overwrite=True)

    Module("r.mask", flags="r")

    ###
    minorMessage("...adding improductive forest, recent fellings, and protected_forests as new LU categories...")
    ###

    # Mask forests

    Module("r.mask", raster=nmd_gen, maskcats="111 thru 127")

    Module("r.mapcalc",
           expression=forest_mod + "= if(" + improductive_forest + "== 2, 130, \
                                       if(" + fellings + "== 1, 131, \
                                       if(" + protected_land + ", 132)))", overwrite=True)

    Module("r.mask", flags="r")

    Module("r.mask", vector=study_area)

    Module("r.null",
           map=forest_mod,
           null=0)

    Module("r.mapcalc",
           expression=nmd_gen_mod + "= if(" + nmd_gen + "== 118, 118, \
                                   if(" + nmd_gen + "== 128, 128, \
                                   if(" + forest_mod + "> 0, " + forest_mod + ", " + nmd_gen + ")))", overwrite=True)

    Module("r.mask", flags="r")

    ###
    minorMessage("...set null outside study area...")
    ###
    Module("r.mask", vector=study_area)

    Module("r.null",
           map=nmd_gen,
           setnull=0)

    ###
    minorMessage("...preparing wetness data...")
    ###

    # NoData cells removed in pre-processing so only clipping to study area here

    Module("g.region", raster=nmd_gen, align=nmd_gen)

    Module("r.mapcalc", expression=wetness + " = " + wetness_raw, overwrite=True)

    ###
    minorMessage("...preparing datasets for calculating statistics on wetlands in selected VMI:s...")
    ###

    Module("g.region", raster=nmd_gen_nobuffer, align=nmd_gen_nobuffer)

    #Create mask: input_VMI. Value: high or very high
    Module("r.mask", flags="r")
    Module("r.mask", vector=VMI_raw, where="KLASS_OBJ < 3 OR  HYD_PAVERK == 0")

    #Create raster for wetlands in selected VMI:s
    Module("r.mapcalc", expression=VMI_wetlands + "=if(" + nmd_gen_nobuffer + "==2,1,0)", overwrite=True)

    Module("r.mask", flags="r")

    ###
    minorMessage("...Creating 20 m datasets...")
    ###

    Module("r.mask", vector=study_area)

    Module("g.region", raster=nmd_gen, res=20)

    Module("r.resample", input=nmd_gen, output=nmd_gen_20m, overwrite=True)

    Module("g.region", raster=nmd_gen, align=nmd_gen)

    Module("r.mapcalc",
        expression=infrastructure + '= if(' + nmd_gen + '== 51, 51, if(' + nmd_gen + '== 52, 52, if(' + nmd_gen + '== 53, 53)))',
        overwrite=True)

    Module("g.region", raster=nmd_gen_20m)

    Module("r.resamp.stats",
        input = infrastructure,
        output = infrastructure_20m,
        method = "maximum",
        overwrite=True)

    Module("r.mapcalc",
        expression=nmd_gen_20m + '= if(' + infrastructure_20m + '>0,' + infrastructure_20m + ',' + nmd_gen_20m + ')',
        overwrite=True)

    Module("r.resamp.stats", input=wetness, output=wetness_20m, overwrite=True)

    Module("r.mask", flags="r")

    ###
    minorMessage("...selecting value cores...")
    ###

    Module("v.select",
        ainput = VMI_raw,
        binput = study_area,
        output = VMI_study_area,
        overwrite=True)

    Module("v.extract",
        input = VMI_study_area,
        output = VMI,
        where = "KLASS_OBJ < 3 OR HYD_PAVERK = 0",
        overwrite=True)


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
    Module("g.region", raster=nmd_gen_nobuffer)

    # Calculate statistics for wetlands in selected VMI:s

    Module("r.mask", raster=VMI_wetlands, maskcats=1)

    ret = Module('r.univar', flags='ge', stdout_=PIPE, map=wetness, quiet=True)
    stats = gscript.parse_key_val(ret.outputs.stdout)

    median = stats["median"]
    std = stats["stddev"]
    mean = stats["mean"]
    print('std: ' + std)
    print('mean: ' + mean)
    mean_int = int(float(mean))
    std_int = int(float(std))
    std_low = mean_int - std_int
    std_high = mean_int + std_int

    # Identify cells inside wetlands in selected VMI:s with mean wetness

    Module("r.mapcalc", expression=optimal_wetness + "= if(" + wetness + "==" + str(mean_int) + ",1)", overwrite=True)

    # 5. Mask cells with mean wetness and randomly create points
    Module("r.mask", flags="r")
    Module("r.mask", raster=optimal_wetness, maskcats=1)

    Module("r.random.cells",
            output=focal_points_ras,
            distance="5000",
            ncells="500",
            seed="1234",  # If omitted, output will differ every time. If set, output will always be the same,
            overwrite=True)

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
           output =export_vector_path + focal_points_vect,
           format = "ESRI_Shapefile")

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
    ecosystem_modification()
    combine_resistance()
    save_resistance()

    majorMessage("...RESISTANCE LAYER CREATED")


def structural_resistance():
    #    Module("r.mask", flags="r")

    Module("g.region", raster=nmd_gen, align=nmd_gen)

    #
    minorMessage(" ...calculating structural resistance based on wetness...")

    Module("r.mask", raster=VMI_wetlands, maskcats=1)

    ret = Module('r.univar', flags='ge', stdout_=PIPE, map=wetness, quiet=True)
    stats = gscript.parse_key_val(ret.outputs.stdout)

    median = stats["median"]
    std = stats["stddev"]
    mean = stats["mean"]
    mean_int = int(float(mean))
    std_int = int(float(std))
    std_low = mean_int - std_int
    std_high = mean_int + std_int
    std_low_str = str(std_low)
    std_high_str = str(std_high)
    miniMessage("mean: " + mean + " | std: " + std + " | lower limit: " + std_low_str +  " | upper limit: " + std_high_str)

    # Module("r.mapcalc", expression=structural_res_wetland + " = if( " + nmd_gen + ", 0)", overwrite=True, quiet=True)

    Module("r.mask", flags="r")

    Module("r.mapcalc", expression=structural_res + " = if( " + \
                                   wetness + " <" + std_low_str + "," + std_low_str + "-" + wetness + ", if(" + \
                                   wetness + " >" + std_high_str + "," + wetness + "-" + std_high_str +", 0))", overwrite=True, quiet=True)

    # Setting 0 to 1. Necessary to run circuitscape

    Module("r.mapcalc", expression=structural_res_corr + " = if( " + structural_res + " == 0, 1," + \
                                   structural_res + ")", overwrite=True, quiet=True)

def ecosystem_modification():
    minorMessage(" ...calculating human influence...")

    # using input reclass file to create raster of ecomod res values. Update input file to change.

    Module("r.reclass",
           input = nmd_gen,
           output = ecosystem_modification_res,
           rules = ecosystem_modification_input,
           overwrite=True)


def combine_resistance():
    minorMessage(" ...calculating statistics...")

    Module("g.region", raster=nmd_gen, align=nmd_gen)

    ret = Module('r.univar', flags='ge', stdout_=PIPE, map=structural_res, quiet=True)
    stats = gscript.parse_key_val(ret.outputs.stdout)
    max_wetness = stats["max"]
    max_wetness_int = int(max_wetness)

    ret = Module('r.univar', flags='ge', stdout_=PIPE, map=ecosystem_modification_res, quiet=True)
    stats = gscript.parse_key_val(ret.outputs.stdout)
    max_ecomod = stats["max"]
    max_ecomod_int = int(max_ecomod)

    weight_ecomod = 0.5
    scaling_factor = max_wetness_int / max_ecomod_int
    max_res = int(max_wetness_int + (max_ecomod_int * scaling_factor * weight_ecomod))

    print("max wetness res: " + max_wetness + ", max ecomod: " + max_ecomod + ", scaling factor: " + str(scaling_factor) + \
          ", max res = " + str(max_res))

    minorMessage(" ...combining resistances...")

    Module("r.mapcalc", expression=structural_res_comb + "= int(" + structural_res + "+ (" + ecosystem_modification_res + \
                                   " * " + str(scaling_factor) + "*" + str(weight_ecomod) + "))", overwrite=True)

    Module("g.region", raster=nmd_gen_20m)

    Module("r.resamp.stats", input=structural_res_comb, output=structural_res_comb_20m, overwrite=True)

    Module("g.region", raster=nmd_gen, align=nmd_gen)

    minorMessage(" ...correcting for infrastructure and sea...")

    Module("r.mapcalc", expression=resistance + "= int(if( "+ structural_res_comb + " < 1, 1, if("  + \
                                   nmd_gen + "== 51 | " + nmd_gen + " ==  52 | " + \
                                   nmd_gen + " == 53 | " + nmd_gen + " ==  62," + str(max_res) + "," + \
                                   structural_res_comb + ")))", overwrite=True)

    Module("g.region", raster=nmd_gen_20m)

    Module("r.mapcalc", expression=resistance_20m + "= int(if( " + structural_res_comb_20m + " < 1, 1, if(" + \
                                   nmd_gen_20m + "== 51 | " + nmd_gen_20m + " ==  52 | " + \
                                   nmd_gen_20m + " == 53 | " + nmd_gen_20m + " ==  62," + str(max_res) + "," + \
                                   structural_res_comb_20m + ")))", overwrite=True)

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
region_info_label = Label(a, text="NB: entire county \n RA: Råneälven\n test: custom test area \n ")
input_buffer_label = Label(a, text="\nSpecify buffer size in meter (Default: 10,000)\n")
buffer_status_label = Label(a, text="Current buffer: " + str(buffer) + " m")
Title_label = Label(a, text="\n\nSelect operation", font=("Courier", 20))
Study_area_label = Label(a, text="\n_______________________________\nDefine study area\n", font=("Courier", 12))
Preparation_label = Label(a, text="\n_______________________________\nPrepare data\n", font=("Courier", 12))
Compute_label = Label(a, text="\n_______________________________\nGenerate Circuitscape input\n", font=("Courier", 12))
Circuitscape_label = Label(a, text="\n_______________________________\nCircuitscape\n", font=("Courier", 12))
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

    buffer_status_label.config(text="Current buffer: " + str(buffer) + " m (" + get_time() + ")")
    buffer_status_label.update_idletasks()


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


def reset_fields():
    labels = [prepare_datasets_label, generate_focal_points_label, compute_resistance_label, generate_init_file_label,
              init_circuitscape_label]

    for label in labels:
        label.config(text="Not completed")
        label.update_idletasks()


textbox_region = Text(a, height=1, width=10)
textbox_buffer = Text(a, height=1, width=10)

# command=lambda: retrieve_input() >>> just means do this when i press the button

save_region_button = Button(a, text="Save", activebackground="black",
                            activeforeground="WHITE", \
                            bg="green", height=1, width=10, command=lambda: retrieve_region())

save_buffer_button = Button(a, text="Save", activebackground="black",
                            activeforeground="WHITE", \
                            bg="green", height=1, width=10, command=lambda: retrieve_buffer())

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

generate_init_file_button = Checkbutton(a, text="Generate init file", activebackground="black",
                                        activeforeground="WHITE", \
                                        bg="green", width=35, bd=10, variable=CheckVar4, onvalue=1, offvalue=0, \
                                        command=generate_init_file)

init_circuitscape_button = Checkbutton(a, text="Initiate Circuitscape", activebackground="black",
                                       activeforeground="WHITE", \
                                       bg="green", width=35, bd=10, variable=CheckVar5, onvalue=1, offvalue=0, \
                                       command=initiate_circuitscape)

reset_button = Checkbutton(a, text="Reset fields", activebackground="black", activeforeground="WHITE", \
                           bg="orange", width=35, bd=10, fg="black", variable=CheckVar12, onvalue=1, offvalue=0, \
                           command=reset_fields)

quit_button = Checkbutton(a, text="Quit", activebackground="black", activeforeground="WHITE", \
                          bg="red", width=35, bd=10, fg="black", variable=CheckVar12, onvalue=1, offvalue=0, \
                          command=a.destroy)

# C5 = Checkbutton(a, text="Calculate SOC increase relative 2020", activebackground="black", activeforeground="WHITE", \
#                  bg="lightgreen", width=35, bd=10, variable=CheckVar5, onvalue=1, offvalue=0, \
#                  command=selected_5)
#
# C6 = Checkbutton(a, text="Calculate new SOC values per ha", activebackground="black", activeforeground="WHITE", \
#                  bg="lightgreen", width=35, bd=10, variable=CheckVar6, onvalue=1, offvalue=0, \
#                  command=selected_6)
#
# C7 = Checkbutton(a, text="Calculate % of max SOC increase", activebackground="black", activeforeground="WHITE", \
#                  bg="lightgreen", width=35, bd=10, variable=CheckVar7, onvalue=1, offvalue=0, \
#                  command=selected_7)
#
# C8 = Checkbutton(a, text="Calculate co-benefits", activebackground="black", activeforeground="WHITE", \
#                  bg="lightgreen", width=35, bd=10, variable=CheckVar8, onvalue=1, offvalue=0, \
#                  command=selected_8)
#
# C9 = Checkbutton(a, text="Calculate all", activebackground="black", activeforeground="WHITE", foreground="WHITE", \
#                  bg="green", width=35, bd=10, variable=CheckVar9, onvalue=1, offvalue=0, \
#                  command=selected_9)
#
# C10 = Checkbutton(a, text="Export to gpkg", activebackground="black", activeforeground="WHITE", \
#                   bg="yellow", width=35, bd=10, variable=CheckVar10, onvalue=1, offvalue=0, \
#                   command=selected_10)
#
# C11 = Checkbutton(a, text="Aggregate and export to csv", activebackground="black", activeforeground="WHITE", \
#                   bg="yellow", width=35, bd=10, variable=CheckVar11, onvalue=1, offvalue=0, \
#                   command=selected_11)
#
# C12 = Checkbutton(a, text="Reset fields", activebackground="black", activeforeground="WHITE", \
#                   bg="RED", width=35, bd=10, variable=CheckVar12, onvalue=1, offvalue=0, \
#                   command=selected_12)
#
# C13 = Checkbutton(a, text="Quit", activebackground="black", activeforeground="WHITE", \
#                   bg="RED", width=35, bd=10, variable=CheckVar12, onvalue=1, offvalue=0, \
#                   command=a.destroy)
#
# C14 = Checkbutton(a, text="Prepare scenarios", activebackground="black", activeforeground="WHITE", \
#                   bg="lightblue", width=35, bd=10, variable=CheckVar12, onvalue=1, offvalue=0, \
#                   command=selected_13)


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
Preparation_label.grid(row=9, column=0)
prepare_datasets_button.grid(row=10, column=0)
prepare_datasets_label.grid(row=10, column=1)

Compute_label.grid(row=12, column=0)
generate_focal_points_button.grid(row=13, column=0)
generate_focal_points_label.grid(row=13, column=1)
compute_resistance_button.grid(row=14, column=0)
compute_resistance_label.grid(row=14, column=1)

Circuitscape_label.grid(row=15, column=0)
generate_init_file_button.grid(row=16, column=0)
generate_init_file_label.grid(row=16, column=1)
init_circuitscape_button.grid(row=17, column=0)
init_circuitscape_label.grid(row=17, column=1)

System_label.grid(row=18, column=0)
reset_button.grid(row=19, column=0)
quit_button.grid(row=20, column=0)

a.mainloop()

if __name__ == "__main__":
    print("test")
