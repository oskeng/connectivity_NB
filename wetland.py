#!/usr/bin/python3.10
#
# Structural connectivity in Norrbotten county
#
# Author: Oskar Englund
# Email: oskar.englund@miun.se
# Github: https://github.com/oskeng/konnektivitet_NB.git
#
######################

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
# Note: Study area set in GUI
#
region = 'NB'
buffer = 10000
size_value_cores = "5"
#####################################################

# imported
study_area_raw = 'input_study_area_raw'
nmd_gen_sv = 'input_nmd_gen_sv'
value_cores = 'input_value_cores'
height_bush_sv = 'input_height_bush_sv'
height_tree_sv = 'input_height_tree_sv'
cover_bush_sv = 'input_cover_bush_sv'
cover_tree_sv = 'input_cover_tree_sv'

# created as model input
study_area = 'calc_study_area_' + region  # Study area with specified buffer
nmd_gen = 'calc_nmd_gen_' + region
nmd_gen_20m = 'calc_nmd_gen_20m_' + region

value_cores_study_area = 'calc_value_cores_' + region

height_bush = 'calc_height_bush_' + region
height_tree = 'calc_height_tree_' + region
cover_bush = 'calc_cover_bush_' + region
cover_tree = 'calc_cover_tree_' + region

focal_points_ras = "calc_focal_points_ras"
focal_points_vect = "calc_focal_points"

raster_list = [height_tree, height_bush, cover_tree, cover_bush]
forest_true = raster_list[2] + "> 0"
str_resistance_raster = []
corr_str_resistance_raster = []
final_str_resistance_raster = []

dict_list = []  # stats from parameters and resistances
dict_list_res = []  # stats from basic str resistance
dict_list_res_corr = []  # stats from adjusted str resistance before rescale
dict_list_res_corr_ds = []  # stats from final adjusted str resistance

for raster in raster_list:
    str_resistance_raster.append(raster + "_resistance")

for raster in str_resistance_raster:
    corr_str_resistance_raster.append(raster + "_corr")

for raster in corr_str_resistance_raster:
    final_str_resistance_raster.append(raster + "_final")

structural_res = 'structural_resistance_' + region
structural_res_corrected = structural_res + "_corr"
structural_res_final = structural_res + "_final"
human_influence_res = 'human_influence_' + region
resistance = 'resistance_' + region
# lists


# created as Circuitscape input
out_value_cores_selected = 'out_value_cores_selected_' + region
out_value_cores_selected_ras = 'out_value_cores_selected_ras_' + region
out_value_cores_selected_ras_20m = 'out_value_cores_selected_ras_20m_' + region

# export paths

export_gpkg_path = "/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Analys/Output/" + region + "/grassout.gpkg"
export_raster_path = "/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Analys/Output/" + region + "/grassout_ras/"
export_circuitscape_path = "/home/oskeng/Dropbox/Jobb/MIUN/Projekt/f3/Konnektivitet/Circutiscape/input/" + region + "/"
export_csv_path = "/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Analys/Output/csv/" + region + "/"


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
    print(Fore.BLUE + "\n######################################################\n")
    print(message)
    print("\n######################################################\n" + Fore.RESET)


def minorMessage(message):
    print(Fore.BLUE + "\n#######################\n")
    print(message)
    print("\n#######################\n" + Fore.RESET)


def miniMessage(message):
    # gscript.core.info("\n\n---> " + message + "\n\n")
    print(Fore.BLUE + "\n")
    print(message)
    print(Fore.RESET)


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

    global study_area_raw
    global study_area

    study_area_raw = 'input_study_area_raw_' + region

    Module("g.region", vector=study_area_raw, res=10, align=nmd_gen_sv)

    ###
    minorMessage("...creating buffer if set to > 0...")
    ###

    if buffer == 0:
        study_area = study_area_raw
    else:
        Module("v.buffer",
               input=study_area_raw,
               output=study_area,
               type="area",
               distance=buffer,
               overwrite=True)

    ###
    minorMessage("...clipping rasters to study area...")
    ###

    Module("g.region", vector=study_area, res=10, align=nmd_gen_sv, zoom=nmd_gen_sv)

    Module("r.mask", vector=study_area)

    Module("r.mapcalc",
           expression=nmd_gen + " = " + nmd_gen_sv, overwrite=True)

    # Set null outside Sweden
    Module("r.null",
           map=nmd_gen,
           setnull=0)

    # Vegetation height/cover data: setting null to zero and clipping to study area

    Module("g.region", raster=nmd_gen)

    zero_to_null_in = [height_tree_sv, height_bush_sv, cover_tree_sv, cover_bush_sv]
    zero_to_null_out = [height_tree, height_bush, cover_tree, cover_bush]
    i = 0

    for raster in zero_to_null_in:
        out_raster = zero_to_null_out[i]

        Module("r.mapcalc",
               expression=out_raster + "= if(" + nmd_gen + ",if(isnull(" + raster + "),0," + raster + "))", overwrite=True)

        Module("r.mapcalc",
               expression=out_raster + " = " + out_raster, overwrite=True)

        i += 1

    # Creating 20 m land use data for study area

    Module("g.region", raster=nmd_gen, res=20)

    Module("r.resample", input=nmd_gen, output=nmd_gen_20m, overwrite=True)

    Module("r.mask", flags="r")

    ###
    minorMessage("...selecting value cores...")
    ###

    # # creating buffer only polygon
    #
    # Module("v.overlay",
    #     ainput = study_area_buffer,
    #     binput = study_area,
    #     operator = "not",
    #     output = buffer,
    #     overwrite=True)

    # selecting value cores in study area, study area + buffer, and buffer only

    # Module("v.select",
    #    ainput = value_cores,
    #    binput = study_area,
    #    output = value_cores_study_area,
    #    overwrite=True)

    # Module("v.select",
    #     ainput=value_cores,
    #     binput=study_area_buffer,
    #     output=value_cores_study_area_buffer,
    #     overwrite=True)

    # Module("v.select",
    #     ainput=value_cores,
    #     binput=buffer,
    #     output=value_cores_buffer,
    #     overwrite=True)

    ###
    majorMessage("...DATASETS PREPARED")
    ###


def focal_points():
    majorMessage("CREATING FOCAL POINTS...")

    create_focal_points()
    # create_focal_points_rasters()
    # save_focal_points()

    majorMessage("...DONE, FOCAL POINTS CREATED")


def create_focal_points():
    start_time = time.time()
    Module("g.region", raster=nmd_gen)

    # 1. Create mask: input_value_cores

    Module("r.mask", vector=value_cores)

    # 2. Calculate statistics for nmd_gen, height_tree, height_bush, cover_tree, cover_bush
    # 3. Save median value + std value as local variables + as csv for all maps

    maps = [nmd_gen, height_tree, height_bush, cover_tree, cover_bush]
    median_values = []
    std_values = []
    std_low_values = []
    std_high_values = []

    for map in maps:
        ret = Module('r.univar', flags='ge', stdout_=PIPE, map=map, quiet=True)
        stats = gscript.parse_key_val(ret.outputs.stdout)

        median = stats["median"]
        std = stats["stddev"]
        std_low = int(median) - int(float(std))
        std_high = int(median) + int(float(std))

        median_values.append(median)
        std_values.append(std)
        std_low_values.append(std_low)
        std_high_values.append(std_high)

    # list of name, degree, score
    nme = ["NMD", "height_tree", "height_bush", "cover_tree", "cover_bush"]

    # dictionary of lists
    dict = {'map': nme, 'median': median_values, 'std': std_values, 'std_low': std_low_values, 'std_high': std_high_values}

    df = pd.DataFrame(dict)

    # saving the dataframe
    df.to_csv(export_csv_path + 'value_core_stats.csv')


    # 5. Check statistics...

    # 6. Identify cells with "perfect" values. Checking also outside of value cores since they are not perfect...

    # Module("r.mask", flags="r")

    potfp_perf_ras = "calc_perfect_potential_focal_points_ras"

    Module("r.mapcalc", expression=potfp_perf_ras +
                      "= if((" + nmd_gen + ">= 111 & " + nmd_gen + "<= 127) & " + nmd_gen + "!= 118" +
                      ",if(" + maps[1] + "== " + "int(" + median_values[1] + ")" +
                      ",if(" + maps[2] + "== " + "int(" + median_values[2] + ")" +
                      ",if(" + maps[3] + "== " + "int(" + median_values[3] + ")" +
                      ",if(" + maps[4] + "== " + "int(" + median_values[4] + ")" +
                      ",1)))))", overwrite=True)

    # 7. Identify cells with "almost perfect" values - Not necessary

    # potfp_ras = "calc_potential_focal_points_ras"
    # Module("r.mapcalc",
    #        expression=potfp_ras +
    #            "= if((" + nmd_gen + ">= 111 & " + nmd_gen + "<= 127) & " + nmd_gen + "!= 118" +
    #            ",if(" + maps[1] + "> " + std_low_values[1] + " &" + maps[1] + "< " + std_high_values[1] +
    #            ",if(" + maps[2] + "> " + std_low_values[2] + " &" + maps[2] + "< " + std_high_values[2] +
    #            ",if(" + maps[3] + "> " + std_low_values[3] + " &" + maps[3] + "< " + std_high_values[3] +
    #            ",1))))", overwrite=True)

    # 8. Randomly select a given number of cells to be used as focal points

    # Module("r.mask", raster=potfp_perf_ras, maskcats="1")

    Module("r.random.cells",
            output=focal_points_ras,
            distance="10000",
            ncells="200",
            seed="100",  # If omitted, output will differ every time. If set, output will always be the same,
            overwrite=True)

    Module("r.mask", flags="r")

    # And save as points to make them easier to assess

    Module("r.to.vect",
            input=focal_points_ras,
            output=focal_points_vect,
            type="point",
            overwrite=True)

    minorMessage("...extracting core_areas...")

    # Module("v.extract",
    #        input=value_cores_study_area,
    #        where="AREA_HA >=" + size_value_cores,
    #        output=out_value_cores_selected,
    #        overwrite=True)
    #
    # # Det finns ev. flera areor med samma cat, varav dubletterna har area noll. Detta resulterar isf i multipla centroider inom samma area. Inte aktuellt i detta fallet men kanske behövs i andra områden
    # #
    # # gscript.core.info("\n ---> resolving potential duplicates...\n \n")
    # #
    # # Module("v.dissolve",
    # #     input=out_value_cores_selected,
    # #     column="cat",
    # #     output=out_value_cores_selected,
    # #     overwrite=True)
    #
    # minorMessage("...calculating LU statistics for selected value cores...")
    #
    # Module("v.rast.stats",
    #        map=out_value_cores_selected,
    #        raster=nmd_gen,
    #        column_prefix="LU",
    #        method="median",
    #        flags="c")
    #
    # minorMessage("...exporting statistics...")
    #
    # gscript.run_command("v.db.select",
    #                     map=out_value_cores_selected,
    #                     file=export_csv_path + "value_cores.csv",
    #                     columns="SKYDDSTYP as skyddstyp, sum(AREA_HA) as sum_area, count(cat) as count, LU_median as LC",
    #                     group="LU_median,SKYDDSTYP",
    #                     overwrite=True)
    #
    # minorMessage("...saving selected value cores to gpkg...")
    #
    # gscript.run_command("v.out.ogr", input=out_value_cores_selected, output=export_gpkg_path, format="GPKG",
    #                     output_layer=out_value_cores_selected, flags='u', overwrite=True)


def create_focal_points_rasters():
    Module("g.region", raster=nmd_gen)

    minorMessage("...creating focal point rasters...")

    Module("v.to.rast",
           input=out_value_cores_selected,
           type='centroid',
           output=out_value_cores_selected_ras,
           use='cat',
           memory='100000',
           overwrite=True)

    Module("g.region", raster=nmd_gen_20m)

    Module("v.to.rast",
           input=out_value_cores_selected,
           type='centroid',
           output=out_value_cores_selected_ras_20m,
           use='cat',
           memory='100000',
           overwrite=True)

    Module("g.region", raster=nmd_gen)

    minorMessage("...removing focal points that are out of bounds...")

    # Module("g.region", raster=nmd_gen_20m)
    # Module("r.mapcalc", expression=out_value_cores_selected_ras_20m + "= " + out_value_cores_selected_ras_20m, overwrite=True)

    # Module("r.mask", flags="r")

    Module("g.region", raster=nmd_gen)


def save_focal_points():
    minorMessage("...saving focal points to Circuitscape format...")

    Module("r.out.gdal",
           input=out_value_cores_selected_ras,
           output="/home/oskeng/Dropbox/Jobb/MIUN/Projekt/f3/Konnektivitet/Circuitscape/input/focal_points.asc",
           format="AAIGrid",
           type="Int32",
           createopt="FORCE_CELLSIZE=YES",
           nodata="-9999",
           flags='mf',
           overwrite=True)

    Module("r.out.gdal",
           input=out_value_cores_selected_ras_20m,
           output="/home/oskeng/Dropbox/Jobb/MIUN/Projekt/f3/Konnektivitet/Circuitscape/input/focal_points_20m.asc",
           format="AAIGrid",
           type="Int32",
           createopt="FORCE_CELLSIZE=YES",
           nodata="-9999",
           flags='mf',
           overwrite=True)


def calc_resistance():
    majorMessage("CREATING RESISTANCE LAYER...")

    structural_resistance()
    human_influence()
    combine_resistance()

    majorMessage("...RESISTANCE LAYER CREATED")


def structural_resistance():
    #    Module("r.mask", flags="r")

    Module("g.region", raster=nmd_gen)

    #
    minorMessage(" ...calculating structural resistance based on tree/bush height/cover...")

    #
    miniMessage("Create empty rasters...")

    Module("r.mapcalc", expression=structural_res + " = if( " + nmd_gen + ", 0)", overwrite=True, quiet=True)

    basic_str_res()

    Module("r.mapcalc", expression=structural_res_corrected + " = if( " + nmd_gen + ", 0)", overwrite=True, quiet=True)

    adjust_str_res()

    #
    miniMessage("Stats for structural resistance values")

    for dictionary in dict_list:
        miniMessage(dictionary)


def basic_str_res():
    # Loop input rasters and calculate mean + stddev within selected value cores.
    # Then calculate resistance based on deviations from mean +- stddev
    # And update resistance raster

    i = 0

    miniMessage("Calculating resistance according to the general principle. Entering loop...")

    for n in range(0, len(raster_list)):

        parameter_ras = raster_list[n]
        basic_res_ras = str_resistance_raster[n]

        # Calculate stats on parameters

        Module("r.mask", vector=out_value_cores_selected, overwrite=True)

        ret = Module('r.univar', flags='g', stdout_=PIPE, map=parameter_ras, quiet=True)
        stats = gscript.parse_key_val(ret.outputs.stdout)

        stddev = stats["stddev"]
        mean = stats["mean"]
        maximum = stats["max"]
        minimum = stats["min"]

        low_limit = float(mean) - float(stddev)
        high_limit = float(mean) + float(stddev)

        if low_limit < 0:
            low_limit = 0

        max_res_high = float(maximum) - float(high_limit)
        max_res_low = low_limit

        dictionary = {"raster": parameter_ras, "max value": str(maximum), "min value": str(minimum),
                      "lower threshold for ZRR": str(low_limit), "upper threshold for ZRR": str(high_limit),
                      "max resistance below ZRR": str(max_res_low),
                      "max resistance above ZRR": str(max_res_high)}

        dict_list.append(dictionary)

        Module("r.mask", flags="r")

        # Calculate basic resistance

        calc_str_res(parameter_ras, basic_res_ras, str(low_limit), str(high_limit), str(low_limit), str(high_limit))

        # Update resistance raster
        update_str_res_ras(basic_res_ras, structural_res)


def adjust_str_res():
    #
    miniMessage("Applying adjustments to structural resistance...")  # See methods

    # Tree height parameters. n = 0
    tree_height_weight = "0.5"
    tree_height_weight_nonforest = "0.5"
    tree_height_ZRR_low = dict_list[0]["lower threshold for ZRR"]
    tree_height_ZRR_high = dict_list[0]["upper threshold for ZRR"]
    tree_height_ZRR_low_nonforest = dict_list[0]["lower threshold for ZRR"]
    tree_height_ZRR_high_nonforest = dict_list[0]["upper threshold for ZRR"]

    # Bush height parameters. n = 1

    bush_height_weight = "0.25"
    bush_height_weight_nonforest = "0.5"
    bush_height_ZRR_low = dict_list[1]["lower threshold for ZRR"]
    bush_height_ZRR_high = dict_list[1]["upper threshold for ZRR"]
    bush_height_ZRR_low_nonforest = dict_list[0]["lower threshold for ZRR"]  # same as for tree height
    bush_height_ZRR_high_nonforest = dict_list[0]["upper threshold for ZRR"]  # same as for tree height

    # Tree cover parameters. n = 2

    tree_cover_weight = "1"
    tree_cover_weight_nonforest = "1"
    tree_cover_ZRR_low = dict_list[2]["lower threshold for ZRR"]
    tree_cover_ZRR_high = dict_list[2]["upper threshold for ZRR"]
    tree_cover_ZRR_low_nonforest = dict_list[2]["lower threshold for ZRR"]
    tree_cover_ZRR_high_nonforest = dict_list[2]["upper threshold for ZRR"]

    # Bush cover parameters. n = 3

    bush_cover_weight = "0.25"
    bush_cover_weight_nonforest = "1"
    bush_cover_ZRR_low = dict_list[3]["lower threshold for ZRR"]
    bush_cover_ZRR_high = dict_list[3]["upper threshold for ZRR"]
    bush_cover_ZRR_low_nonforest = dict_list[2]["lower threshold for ZRR"]  # same as for tree cover
    bush_cover_ZRR_high_nonforest = dict_list[2]["upper threshold for ZRR"]  # same as for tree cover

    max_forest_cover_res = dict_list[2]["max resistance below ZRR"]

    weight_list = [tree_height_weight, bush_height_weight, tree_cover_weight, bush_cover_weight]
    weight_list_nonforest = [tree_height_weight_nonforest, bush_height_weight_nonforest, tree_cover_weight_nonforest,
                             bush_cover_weight_nonforest]
    ZRR_low_list = [tree_height_ZRR_low, bush_height_ZRR_low, tree_cover_ZRR_low, bush_cover_ZRR_low]
    ZRR_high_list = [tree_height_ZRR_high, bush_height_ZRR_high, tree_cover_ZRR_high, bush_cover_ZRR_high]
    ZRR_low_nonforest_list = [tree_height_ZRR_low_nonforest, bush_height_ZRR_low_nonforest,
                              tree_cover_ZRR_low_nonforest, bush_cover_ZRR_low_nonforest]
    ZRR_high_nonforest_list = [tree_height_ZRR_high_nonforest, bush_height_ZRR_high_nonforest,
                               tree_cover_ZRR_high_nonforest, bush_cover_ZRR_high_nonforest]

    print(ZRR_low_list)
    print(ZRR_high_list)
    print(ZRR_low_nonforest_list)
    print(ZRR_high_nonforest_list)

    for n in range(0, len(raster_list)):
        parameter_raster = raster_list[n]
        basic_res_ras = str_resistance_raster[n]
        corr_res_ras = corr_str_resistance_raster[n]
        final_res_ras = final_str_resistance_raster[n]

        # Calculate stats on corrected resistance

        Module("r.mask", vector=out_value_cores_selected, overwrite=True)

        ret = Module('r.univar', flags='g', stdout_=PIPE, map=basic_res_ras, quiet=True)
        stats = gscript.parse_key_val(ret.outputs.stdout)

        maximum_res = stats["max"]
        minimum_res = stats["min"]
        mean_res = stats["mean"]

        dictionary = {"raster": basic_res_ras, "max resistance": str(maximum_res),
                      "min resistance": str(minimum_res), "mean resistance": str(mean_res)}

        dict_list.append(dictionary)

        Module("r.mask", flags="r")

        # Adjust resistance

        calc_str_res(parameter_raster, corr_res_ras, ZRR_low_list[n], ZRR_high_list[n], ZRR_low_nonforest_list[n],
                     ZRR_high_nonforest_list[n])

        # Calculate stats on corrected resistance

        Module("r.mask", vector=out_value_cores_selected, overwrite=True)

        ret = Module('r.univar', flags='g', stdout_=PIPE, map=corr_res_ras, quiet=True)
        stats = gscript.parse_key_val(ret.outputs.stdout)

        maximum_res = stats["max"]
        minimum_res = stats["min"]
        mean_res = stats["mean"]

        dictionary = {"raster": corr_res_ras, "max resistance": str(maximum_res),
                      "min resistance": str(minimum_res), "mean resistance": str(mean_res), "rescaled": "No"}

        dict_list.append(dictionary)

        Module("r.mask", flags="r")

        # Downscale

        rescale_str_res(corr_res_ras, weight_list[n], weight_list_nonforest[n], max_forest_cover_res, str(maximum_res),
                        final_res_ras)

        # Calculate stats on corrected and rescaled resistance

        Module("r.mask", vector=out_value_cores_selected, overwrite=True)

        ret = Module('r.univar', flags='g', stdout_=PIPE, map=final_res_ras, quiet=True)
        stats = gscript.parse_key_val(ret.outputs.stdout)

        maximum_res = stats["max"]
        minimum_res = stats["min"]
        mean_res = stats["mean"]

        dictionary = {"raster": final_res_ras, "max resistance": str(maximum_res),
                      "min resistance": str(minimum_res), "mean resistance": str(mean_res), "rescaled": "Yes"}

        dict_list.append(dictionary)

        Module("r.mask", flags="r")

        update_str_res_ras(corr_res_ras, structural_res_corrected)
        update_str_res_ras(final_res_ras, structural_res_final)

    #
    miniMessage("saving structural resistance raster...")

    Module("r.out.gdal", input=structural_res, output=export_raster_path + structural_res + ".tif", type="Float64",
           overwrite=True, quiet=True)

    #
    minorMessage("...structural resistance calculated")


def calc_str_res(parameter_ras, res_ras, low_limit, high_limit, low_limit_nonforest, high_limit_nonforest):
    #
    miniMessage("Calculating " + parameter_ras + "...")

    Module("r.mapcalc", expression=res_ras + "= if( " + forest_true + "," +
                                   "if (" + parameter_ras + " < " + low_limit + ", " + low_limit + " - " + parameter_ras + ", if (" + parameter_ras + " > " + high_limit + ", " + parameter_ras + "-" + high_limit + ",0))," +
                                   "if (" + parameter_ras + " < " + low_limit_nonforest + ", " + low_limit_nonforest + " - " + parameter_ras + ", if (" + parameter_ras + " > " + high_limit_nonforest + ", " + parameter_ras + "-" + high_limit_nonforest + ",0)))",
           overwrite=True)

    Module("r.mapcalc",  # setting minus to zero
           expression=res_ras + "= if(" + res_ras + "< 0, 0," + res_ras + ")",
           overwrite=True, quiet=True)


def rescale_str_res(ras_to_rescale, weight, weight_nonforest, max_fc_res, max_parameter_res, output):
    if raster == corr_str_resistance_raster[3]:
        print(weight + weight_nonforest + max_fc_res + max_parameter_res)

    Module("r.mapcalc", expression=output + "= if( " + forest_true + "," +
                                   ras_to_rescale + "*" + max_fc_res + "*" + weight + "/" + max_parameter_res + "," +
                                   ras_to_rescale + "*" + max_fc_res + "*" + weight_nonforest + "/" + max_parameter_res + ")",
           overwrite=True)


def update_str_res_ras(res_ras, output):
    miniMessage("Updating structural resistance raster")

    Module("r.mapcalc", expression=output + "=" + structural_res + "+" + res_ras,
           overwrite=True, quiet=True)


def human_influence():
    minorMessage(" ...calculating human influence...")

    # Create empty raster

    Module("r.mapcalc", expression=human_influence_res + " = if(" + nmd_gen + ", 0)", overwrite=True)

    Module("r.out.gdal", input=human_influence_res, output=export_raster_path + human_influence_res + ".tif",
           type="Float64",
           overwrite=True, quiet=True)


def combine_resistance():
    minorMessage(" ...combining resistances...")

    Module("r.mapcalc", expression=resistance + "=" + structural_res + "+" + human_influence_res,
           overwrite=True)

    Module("r.out.gdal", input=resistance, output=export_raster_path + resistance + ".tif", type="Float64",
           overwrite=True, quiet=True)


def generate_init():
    Module("g.region", raster=nmd_gen)
    gscript.core.info("\n ---> Nope, not yet...\n \n")
    return


def init_circuitscape():
    Module("g.region", raster=nmd_gen)
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
input_region_label = Label(a, text="Input region here: NB or test. (Default: NB)\n")
region_status_label = Label(a, text="Current region: " + region)
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

# def selected_1():
#     start_time = time.time()
#
#     generate_focal_points_label.config(text=running)
#     generate_focal_points_label.update_idletasks()
#
#     start_over()
#
#     generate_focal_points_label.config(text=completed + get_time())
#     generate_focal_points_label.update_idletasks()
#
#     labels = [compute_resistance_label, generate_init_file_label, init_circuitscape_label, L5, L6, L7, L8, L9, generate_focal_points_label0, generate_focal_points_label1, generate_focal_points_labecompute_resistance_label]
#
#     for label in labels:
#         label.config(text="Not completed")
#         label.update_idletasks()
def retrieve_region():
    global region
    region = textbox_region.get("1.0", 'end-1c')
    region_status_label.config(text="Current region: " + region + " (" + get_time() + ")")
    region_status_label.update_idletasks()


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


# def selected_8():
#     L8.config(text=running + " (1/4: water erosion)")
#     L8.update_idletasks()
#
#     water_erosion()
#
#     L8.config(text=running + " (2/4: wind erosion)")
#     L8.update_idletasks()
#
#     wind_erosion()
#
#     L8.config(text=running + " (3/4: N emissions)")
#     L8.update_idletasks()
#
#     N_emissions()
#
#     L8.config(text=running + " (4/4: Flooding)")
#     L8.update_idletasks()
#
#     flooding()
#
#     L8.config(text=completed + get_time())
#     L8.update_idletasks()

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
