#!/usr/bin/env python3
#
# Structural connectivity in Norrbotten county: forests
#
# Author: Oskar Englund
# Email: oskar.englund@miun.se
# Github: https://github.com/oskeng/connectivity_NB.git
#

import sys
import os
import subprocess
from datetime import datetime
from tkinter import Tk, Label, Text, Button, Checkbutton, IntVar, filedialog as fd

#####################################################
# Initialize GRASS GIS Environment



# Set paths to GRASS GIS installation and data
# Update these paths according to your system configuration
gisbase = '/opt/grass'  # Path to GRASS GIS installation
gisdb = '/home/oskeng/Dropbox/Jobb/GIS/grassdata'  # Path to GRASS GIS database
location = 'Sweref99'  # Name of your GRASS location
mapset = 'connectivity_forest_new'  # Name of the mapset

# path to the GRASS GIS launch script
# we assume that the GRASS GIS start script is available and on PATH
# query GRASS itself for its GISBASE
# (with fixes for specific platforms)
# needs to be edited by the user
executable = "grass"

# query GRASS GIS itself for its Python package path
grass_cmd = [executable, "--config", "python_path"]
process = subprocess.run(grass_cmd, check=True, text=True, stdout=subprocess.PIPE)

# define GRASS-Python environment
sys.path.append(process.stdout.strip())

# import (some) GRASS Python bindings
import grass.script as gs
from grass.pygrass.modules import Module

# launch session
session = gs.setup.init(gisdb, location, mapset)


#####################################################
# Default values - study area can be set in GUI

region = ''
buffer = ''
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
resistance_cities = '100'

#####################################################

# Necessary input data to be placed in the active mapset
nmd_gen_sv = 'nmd_gen_sv_updated@update_NMD'
input_HCV_kskog = 'out_input_HCV_kskog_final@HCV_kskog'
input_density_HCV = 'input_result_density_forest_HCV_kskog_NB_250m_v2'
study_area_raw = ''
input_tatorter = 'input_tatorter_2020'

# Paths
export_raster_path = ''
export_vector_path = ''
circuitscape_path = ''

# Variables to be set based on the selected region
def set_variables(region):
    suffix = str(output_suffix)

    datasets = {
        'nmd_gen': f"{region}_calc_nmd_gen",
        'nmd_gen_20m': f"{region}_calc_nmd_gen_20m",
        'nmd_gen_nobuffer': f"{region}_calc_nmd_gen_nobuffer",
        'study_area_raw': f"input_study_area_raw_{region}",
        'study_area': f"{region}_study_area",
        'HCV_kskog': f"{region}_HCV_kskog",
        'wetland_forest': f"{region}_wetland_forest",
        'other_forest': f"{region}_other_forest",
        'other_NV': f"{region}_other_NV",
        'nonnat_veg': f"{region}_nonnat_veg",
        'no_veg': f"{region}_no_veg",
        'density_HCV': f"{region}_density_HCV",
        'HCV_density_res': f"{region}_HCV_density_res",
        'wetland_forest_res_ras': f"{region}_wetland_forest_res_ras",
        'other_NV_res_ras': f"{region}_other_NV_res_ras",
        'other_forest_res_ras': f"{region}_other_forest_res_ras",
        'nonnat_veg_res_ras': f"{region}_nonnat_veg_res_ras",
        'no_veg_res_ras': f"{region}_no_veg_res_ras",
        'tatorter': f"{region}_tatorter",
        'resistance': f"out_{region}_calc_resistance_{suffix}",
        'resistance_20m': f"out_{region}_calc_resistance_20m_{suffix}",
    }

    base_path = f"/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Analys/Output/Forest/new/{region}"
    paths = {
        'export_raster_path': f"{base_path}/grassout_ras/",
        'export_vector_path': f"{base_path}/grassout_vect/",
        'circuitscape_path': f"/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Analys/Omniscape/Forest/new/{region}/",
    }

    log_message(f"Variables set for region: {region}")

    return datasets, paths

################################################
# General functions
################################################

def get_time():
    now = datetime.now()
    return now.strftime("%H:%M:%S")

def log_message(message, level="info"):
    flags = "w" if level == "warning" else ""
    Module("g.message", message=f"\n{message}\n", flags=flags)

################################################
# Model functions
################################################

def datasets_func(datasets):
    log_message("PREPARING DATASETS...", "warning")

    Module("g.region", vector=study_area_raw, res=10, align=nmd_gen_sv, zoom=nmd_gen_sv)

    log_message("Creating buffered study area if buffer > 0...")
    Module("v.buffer", input=study_area_raw, output=datasets['study_area'], type="area", distance=buffer, overwrite=True)

    log_message("Creating input data clipped to study area...")
    Module("g.region", vector=datasets['study_area'], res=10, align=nmd_gen_sv, zoom=nmd_gen_sv)
    Module("r.mask", vector=datasets['study_area'])

    log_message(f"Creating {datasets['nmd_gen']}...")
    Module("r.mapcalc", expression=f"{datasets['nmd_gen']} = {nmd_gen_sv}", overwrite=True)

    log_message(f"Creating {datasets['HCV_kskog']}...")
    Module("r.mapcalc", expression=f"{datasets['HCV_kskog']} = {input_HCV_kskog}", overwrite=True)
    Module("r.null", map=datasets['HCV_kskog'], null=0)

    log_message(f"Creating {datasets['other_forest']}...")
    Module("r.mapcalc", expression=f"{datasets['other_forest']} = if({datasets['nmd_gen']} != 118 & {datasets['nmd_gen']} != 128 & {datasets['nmd_gen']} != 130 & {datasets['nmd_gen']} > 110 & {datasets['HCV_kskog']} == 0, 1, 0)", overwrite=True)

    log_message(f"Creating {datasets['other_NV']}...")
    Module("r.mapcalc", expression=f"{datasets['other_NV']} = if(({datasets['nmd_gen']} == 2) | ({datasets['nmd_gen']} == 42), 1, 0)", overwrite=True)

    log_message(f"Creating {datasets['nonnat_veg']}...")
    Module("r.mapcalc", expression=f"{datasets['nonnat_veg']} = if(({datasets['nmd_gen']} == 3) | ({datasets['nmd_gen']} == 54) | ({datasets['nmd_gen']} == 118) | ({datasets['nmd_gen']} == 128) | ({datasets['nmd_gen']} == 130), 1, 0)", overwrite=True)

    log_message(f"Creating {datasets['no_veg']}...")
    Module("r.mapcalc", expression=f"{datasets['no_veg']} = if(({datasets['nmd_gen']} == 41) | ({datasets['nmd_gen']} == 51) | ({datasets['nmd_gen']} == 52) | ({datasets['nmd_gen']} == 53) | ({datasets['nmd_gen']} == 61) | ({datasets['nmd_gen']} == 62), 1, 0)", overwrite=True)

    log_message(f"Creating {datasets['wetland_forest']}...")
    Module("r.mapcalc", expression=f"{datasets['wetland_forest']} = if({datasets['nmd_gen']} > 120 & {datasets['nmd_gen']} < 128, 1, 0)", overwrite=True)

    log_message(f"Creating {datasets['density_HCV']}...")
    Module("r.mapcalc", expression=f"{datasets['density_HCV']} = {input_density_HCV}", overwrite=True)
    Module("r.null", map=input_density_HCV, null=0)

    log_message(f"Creating {datasets['tatorter']}...")
    Module("v.to.rast", input=input_tatorter, output=datasets['tatorter'], use='val', value=resistance_cities, memory=30000, overwrite=True)
    Module("r.null", map=datasets['tatorter'], null=0)

    Module("r.mask", flags="r")

    log_message(f"Creating {datasets['nmd_gen_nobuffer']}...")
    Module("r.mask", vector=study_area_raw)
    Module("r.mapcalc", expression=f"{datasets['nmd_gen_nobuffer']} = {datasets['nmd_gen']}", overwrite=True)
    Module("r.null", map=datasets['nmd_gen_nobuffer'], setnull=0)
    Module("r.mask", flags="r")

    log_message(f"Creating {datasets['nmd_gen_20m']} with 20 m resolution...")
    Module("r.mask", vector=datasets['study_area'])
    Module("g.region", raster=datasets['nmd_gen'], res=20)
    Module("r.resample", input=datasets['nmd_gen'], output=datasets['nmd_gen_20m'], overwrite=True)
    Module("r.mask", flags="r")

    log_message("DATASETS PREPARED", "warning")

def calc_resistance_func(datasets):
    log_message("CREATING RESISTANCE LAYER...", "warning")

    structural_resistance(datasets)
    save_resistance(datasets)

    log_message("RESISTANCE LAYER CREATED", "warning")

def structural_resistance(datasets):
    Module("g.region", raster=datasets['nmd_gen'], align=datasets['nmd_gen'])
    log_message("Creating resistance input maps...")

    Module("r.mapcalc", expression=f"{datasets['HCV_density_res']} = if({datasets['HCV_kskog']} > 0, int((100 - float({datasets['density_HCV']})) / 10 + 1.99), 9999)", overwrite=True)

    Module("r.mapcalc", expression=f"{datasets['wetland_forest_res_ras']} = if({datasets['wetland_forest']} > 0, {wetland_forest_res}, 9999)", overwrite=True)
    Module("r.mapcalc", expression=f"{datasets['other_NV_res_ras']} = if({datasets['other_NV']} > 0, {other_NV_res}, 9999)", overwrite=True)
    Module("r.mapcalc", expression=f"{datasets['other_forest_res_ras']} = if({datasets['other_forest']} > 0, {other_forest_res}, 9999)", overwrite=True)
    Module("r.mapcalc", expression=f"{datasets['nonnat_veg_res_ras']} = if(({datasets['nonnat_veg']} > 0) | ({datasets['nmd_gen']} == 54), {nonnat_veg_res}, 9999)", overwrite=True)
    Module("r.mapcalc", expression=f"{datasets['no_veg_res_ras']} = if({datasets['no_veg']} > 0, {no_veg_res}, 9999)", overwrite=True)

    log_message("Combining input resistance maps...")
    Module("r.series", input=f"{datasets['HCV_density_res']},{datasets['wetland_forest_res_ras']},{datasets['other_NV_res_ras']},{datasets['other_forest_res_ras']}", output="temp_resistance", method='minimum', overwrite=True)
    Module("r.mapcalc", expression=f"temp_resistance_1 = if({datasets['no_veg_res_ras']} < 9999, {datasets['no_veg_res_ras']}, if({datasets['nonnat_veg_res_ras']} < 9999, {datasets['nonnat_veg_res_ras']}, temp_resistance))", overwrite=True)
    Module("r.mapcalc", expression=f"{datasets['resistance']} = temp_resistance_1 + {datasets['tatorter']}", overwrite=True)
    Module("r.null", map=datasets['resistance'], setnull=9999)

    Module("g.region", raster=datasets['nmd_gen_20m'])
    Module("r.mapcalc", expression=f"{datasets['resistance_20m']} = {datasets['resistance']}", overwrite=True)
    Module("g.region", raster=datasets['nmd_gen'], align=datasets['nmd_gen'])

def save_resistance(datasets):
    Module("g.region", raster=datasets['nmd_gen'])
    log_message("Saving resistance layer as GeoTIFF and ASCII...")

    Module("r.out.gdal", input=datasets['resistance'], output=export_raster_path + datasets['resistance'] + ".tif", type="Float64", overwrite=True)
    Module("r.out.gdal", flags="mf", input=datasets['resistance'], output=circuitscape_path + datasets['resistance'] + ".asc", format="AAIGrid", type="Int16", createopt="FORCE_CELLSIZE=TRUE", nodata=-9999, overwrite=True)

    Module("g.region", raster=datasets['nmd_gen_20m'])
    Module("r.out.gdal", input=datasets['resistance_20m'], output=export_raster_path + datasets['resistance_20m'] + ".tif", type="Float64", overwrite=True)
    Module("r.out.gdal", flags="mf", input=datasets['resistance_20m'], output=circuitscape_path + datasets['resistance_20m'] + ".asc", format="AAIGrid", type="Int16", createopt="FORCE_CELLSIZE=TRUE", nodata=-9999, overwrite=True)

def post_processing_func(datasets):
    log_message("STARTING POST-PROCESSING...", "warning")

    cumcur_import = f"omni_norm_cumcur_{region}_{output_suffix}"
    cumcur_import_resamp = f"{cumcur_import}_resamp"
    cumcur_import_resamp_clip = f"{cumcur_import_resamp}_clip"
    cumcur_import_resamp_class = f"{cumcur_import_resamp_clip}_class"

    Module("g.region", vector=datasets['study_area'], res=10, align=datasets['nmd_gen'])
    Module("r.mask", raster=datasets['nmd_gen'], maskcats="62", flags="i")

    log_message("Importing and resampling cumulative current map...")
    Module("r.import", input=cumcur, output=cumcur_import, overwrite=True, flags="o")
    Module("r.resamp.interp", overwrite=True, input=cumcur_import, output=cumcur_import_resamp, method="lanczos")

    log_message("Clipping to study area...")
    Module("g.region", vector=study_area_raw, res=10, align=datasets['nmd_gen'])
    Module("r.mask", flags="r")
    Module("r.mask", vector=study_area_raw)
    Module("r.mapcalc", expression=f"{cumcur_import_resamp_clip} = {cumcur_import_resamp}", overwrite=True)
    Module("r.null", map=cumcur_import_resamp_clip, setnull=0)

    log_message("Classifying using quantiles...")
    post_processing_path = f"/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Analys/Omniscape/Forest/new/{region}/post_processing/"
    Module("r.quantile", flags="r", overwrite=True, input=cumcur_import_resamp_clip, quantiles=10, file=post_processing_path + 'quantiles.txt')
    Module("r.recode", input=cumcur_import_resamp_clip, output=cumcur_import_resamp_class, rules=post_processing_path + 'quantiles.txt', overwrite=True)
    Module("r.out.gdal", input=cumcur_import_resamp_class, output=post_processing_path + f'classified_norm_cumcur_{region}_{output_suffix}.tif', type="Int32", overwrite=True)

    Module("r.mask", flags="r")
    log_message("POST-PROCESSING COMPLETED", "warning")

################################################
# GUI Functions
################################################

def retrieve_region():
    global region
    region = textbox_region.get("1.0", 'end-1c') or 'NB'
    region_status_label.config(text=f"Current region: {region} ({get_time()})")
    datasets, paths = set_variables(region)
    globals().update(datasets)
    globals().update(paths)

def retrieve_buffer():
    global buffer
    buffer = textbox_buffer.get("1.0", 'end-1c') or '10000'
    buffer_status_label.config(text=f"Current buffer: {buffer} m ({get_time()})")

def retrieve_suffix():
    global output_suffix
    output_suffix = textbox_suffix.get("1.0", 'end-1c')
    suffix_status_label.config(text=f"Current suffix: {output_suffix} ({get_time()})")

def prepare_datasets_action():
    prepare_datasets_label.config(text="Running...")
    datasets, _ = set_variables(region)
    datasets_func(datasets)
    prepare_datasets_label.config(text=f"Completed: {get_time()}")

def compute_resistance_action():
    global wetland_forest_res, other_forest_res, other_NV_res, nonnat_veg_res, no_veg_res

    wetland_forest_res = textbox_wetland_forest_res.get("1.0", 'end-1c') or wetland_forest_res_def
    other_forest_res = textbox_other_forest_res.get("1.0", 'end-1c') or other_forest_res_def
    other_NV_res = textbox_other_NV_res.get("1.0", 'end-1c') or other_NV_res_def
    nonnat_veg_res = textbox_nonnat_veg_res.get("1.0", 'end-1c') or nonnat_veg_res_def
    no_veg_res = textbox_no_veg_res.get("1.0", 'end-1c') or no_veg_res_def

    compute_resistance_label.config(text="Running...")
    datasets, _ = set_variables(region)
    calc_resistance_func(datasets)
    compute_resistance_label.config(text=f"Completed: {get_time()}")

def start_post_processing():
    global cumcur
    cumcur = fd.askopenfilename()
    datasets, _ = set_variables(region)
    post_processing_func(datasets)

def reset_fields():
    labels = [prepare_datasets_label, compute_resistance_label]
    for label in labels:
        label.config(text="Not completed")

def quit_application():
    root.destroy()

################################################
# GUI Layout
################################################

root = Tk()
root.geometry("800x800")
root.title("Structural Connectivity Analysis")

# Labels
input_region_label = Label(root, text="Input region here (Default: NB):")
region_status_label = Label(root, text="Current region: " + region)
region_info_label = Label(root, text="NB (entire county)\nRA: (Råneälven)\ntest_sundom\ntest_gallivare\ntest_granlandet")
input_buffer_label = Label(root, text="Specify buffer size in meters (Default: 10,000):")
buffer_status_label = Label(root, text="Current buffer: " + str(buffer))
input_suffix_label = Label(root, text="Specify suffix for output:")
suffix_status_label = Label(root, text="Current suffix: " + str(output_suffix))
Title_label = Label(root, text="Select Operation", font=("Courier", 20))
Study_area_label = Label(root, text="Define Study Area", font=("Courier", 12))
Preparation_label = Label(root, text="Prepare Data", font=("Courier", 12))
Compute_label = Label(root, text="Generate Circuitscape Input", font=("Courier", 12))
resistance_label = Label(root, text="Resistance values")
label_wetland_forest_res = Label(root, text="Forest on wetland:")
label_other_forest_res = Label(root, text="Other forest:")
label_other_NV_res = Label(root, text="Other natural vegetation:")
label_nonnat_veg_res = Label(root, text="Non-natural vegetation:")
label_no_veg_res = Label(root, text="No vegetation:")
Post_processing_label = Label(root, text="Post Processing", font=("Courier", 12))
System_label = Label(root, text="System", font=("Courier", 12))
prepare_datasets_label = Label(root, text="Not completed")
compute_resistance_label = Label(root, text="Not completed")

# Textboxes
textbox_region = Text(root, height=1, width=10)
textbox_buffer = Text(root, height=1, width=10)
textbox_suffix = Text(root, height=1, width=10)
textbox_wetland_forest_res = Text(root, height=1, width=10)
textbox_other_forest_res = Text(root, height=1, width=10)
textbox_other_NV_res = Text(root, height=1, width=10)
textbox_nonnat_veg_res = Text(root, height=1, width=10)
textbox_no_veg_res = Text(root, height=1, width=10)

# Buttons
save_region_button = Button(root, text="Save", bg="green", command=retrieve_region)
save_buffer_button = Button(root, text="Save", bg="green", command=retrieve_buffer)
save_suffix_button = Button(root, text="Save", bg="green", command=retrieve_suffix)
prepare_datasets_button = Checkbutton(root, text="Prepare Datasets", bg="green", command=prepare_datasets_action)
compute_resistance_button = Checkbutton(root, text="Compute Resistance Layer", bg="green", command=compute_resistance_action)
post_processing_button = Checkbutton(root, text="Run Post Processing", bg="green", command=start_post_processing)
reset_button = Button(root, text="Reset Fields", bg="orange", command=reset_fields)
quit_button = Button(root, text="Quit", bg="red", command=quit_application)

# Layout
Title_label.grid(row=0, column=0, pady=10)
Study_area_label.grid(row=1, column=0, pady=5)

input_region_label.grid(row=2, column=0, sticky='w')
textbox_region.grid(row=2, column=1)
region_status_label.grid(row=2, column=2)
region_info_label.grid(row=2, column=3)
save_region_button.grid(row=2, column=4)

input_buffer_label.grid(row=3, column=0, sticky='w')
textbox_buffer.grid(row=3, column=1)
buffer_status_label.grid(row=3, column=2)
save_buffer_button.grid(row=3, column=4)

input_suffix_label.grid(row=4, column=0, sticky='w')
textbox_suffix.grid(row=4, column=1)
suffix_status_label.grid(row=4, column=2)
save_suffix_button.grid(row=4, column=4)

Preparation_label.grid(row=5, column=0, pady=5)
prepare_datasets_button.grid(row=6, column=0, sticky='w')
prepare_datasets_label.grid(row=6, column=1)

Compute_label.grid(row=7, column=0, pady=5)
resistance_label.grid(row=8, column=1)
label_wetland_forest_res.grid(row=9, column=0)
textbox_wetland_forest_res.grid(row=9, column=1)
label_other_NV_res.grid(row=10, column=0)
textbox_other_NV_res.grid(row=10, column=1)
label_other_forest_res.grid(row=11, column=0)
textbox_other_forest_res.grid(row=11, column=1)
label_nonnat_veg_res.grid(row=12, column=0)
textbox_nonnat_veg_res.grid(row=12, column=1)
label_no_veg_res.grid(row=13, column=0)
textbox_no_veg_res.grid(row=13, column=1)
compute_resistance_button.grid(row=14, column=0, sticky='w')
compute_resistance_label.grid(row=14, column=1)

Post_processing_label.grid(row=15, column=0, pady=5)
post_processing_button.grid(row=16, column=0, sticky='w')

System_label.grid(row=17, column=0, pady=5)
reset_button.grid(row=18, column=0, sticky='w')
quit_button.grid(row=19, column=0, sticky='w')

root.mainloop()