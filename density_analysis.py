#!/usr/bin/python3.11
#
# Identifies areas with a given density of protected, restricted, or continuity forest within a given radius from each cell
#
# Author: Oskar Englund
# Email: oskar.englund@miun.se
# Github: https://github.com/oskeng/konnektivitet_NB.git
#
######################
from typing import Any

import sys
import math
from grass.pygrass.modules import Module

nmd_gen_study_area = 'nmd_gen_study_area'  # generated using density_analysis_nmd.py (see documentation)

Module("g.region", raster='nmd_gen_study_area')

def tot_density(radius_int):

    area = pow(radius_int,2) * math.pi
    area_cells = area / 100  # number of 10 m cells in the circle
    radius = str(radius_int)
    area_str = str(area)
    area_cells_str = str(area_cells)

    Module("g.message", message="\n \n Calculating share of HCV forest in a " + radius + " m search radius. Area is: " + area_str + " m, containing " + area_cells_str + " 10 m cells \n \n")

    input_HCV = "output_HCV_" + radius + "m_v2@density_analysis_count_HCV"
    input_HCV_kskog = "output_HCV_kskog_" + radius + "m_v2@density_analysis_count_HCV_kskog"

    HCV_density_tot = "result_density_tot_HCV_" + radius + "m_v2"
    HCV_kskog_density_tot = "result_density_tot_HCV_kskog_" + radius + "m_v2"

    HCV_expression = HCV_density_tot + "= int(double(" + input_HCV + ") / " + area_cells_str + " * 100)"
    HCV_kskog_expression = HCV_kskog_density_tot + "= int(double(" + input_HCV_kskog + ") / " + area_cells_str + " * 100)"


    Module("g.message", message="\n \n" + HCV_expression + "\n \n")
    Module("g.message", message="\n \n" + HCV_kskog_expression + "\n \n")

    Module("r.mapcalc",
           expression=HCV_expression, overwrite=True)
    Module("r.mapcalc",
           expression=HCV_kskog_expression, overwrite=True)

    Module("r.out.gdal", input=HCV_density_tot,
           output='/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Täthetsanalys/results/total_density/' + HCV_density_tot + '.tif',
           format="GTiff", overwrite=True)
    Module("r.out.gdal", input=HCV_kskog_density_tot,
           output='/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Täthetsanalys/results/total_density/' + HCV_kskog_density_tot + '.tif',
           format="GTiff", overwrite=True)

def forest_density(radius_int):

    radius = str(radius_int)
    Module("g.message", message="\n \n Calculating densities for " + radius + " m search radius \n \n")

    input_forest = "output_forest_" + radius + "m_v2@density_analysis_count_forest"
    input_HCV = "output_HCV_" + radius + "m_v2@density_analysis_count_HCV"
    input_HCV_kskog = "output_HCV_kskog_" + radius + "m_v2@density_analysis_count_HCV_kskog"

    HCV_density = "result_density_forest_HCV_" + radius + "m_v2"
    HCV_kskog_density = "result_density_forest_HCV_kskog_" + radius + "m_v2"

    HCV_expression = HCV_density + "= int(double(" + input_HCV + ") / double(" + input_forest + ") * 100)"
    HCV_kskog_expression = HCV_kskog_density + "= int(double(" + input_HCV_kskog + ") / double(" + input_forest + ") * 100)"

    Module("g.message", message="\n \n" + HCV_expression + "\n \n")
    Module("g.message", message="\n \n" + HCV_kskog_expression + "\n \n")

    Module("r.mapcalc",
           expression=HCV_expression, overwrite=True)
    Module("r.mapcalc",
           expression=HCV_kskog_expression, overwrite=True)

    Module("r.out.gdal", input=HCV_density,
           output='/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Täthetsanalys/results/forest_density/' + HCV_density + '.tif',
           format="GTiff", overwrite=True)
    Module("r.out.gdal", input=HCV_kskog_density,
           output='/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Täthetsanalys/results/forest_density/' + HCV_kskog_density + '.tif',
           format="GTiff", overwrite=True)
def vardetrakter(radius_int, percentage_int): # density of HCV forests (% of forest land). Agriculture, urban land (except roads and transmission lanes) and sea excluded.

    radius = str(radius_int)
    percentage = str(percentage_int)

    Module("g.message", message="\n \n Identifying areas with forest density > " + percentage + " % for a " + radius + " m search radius. Excluding agriculture, sea, and urban land (not roads or transmission lanes). \n \n")

    HCV_density = "result_density_forest_HCV_" + radius + "m_v2"
    HCV_kskog_density = "result_density_forest_HCV_kskog_" + radius + "m_v2"

    HCV_value_cores = "result_vardetrakter_" + percentage + "_HCV_" + radius
    HCV_kskog_value_cores = "result_vardetrakter_" + percentage + "_HCV_kskog_" + radius

    HCV_expression = HCV_value_cores + " = if(" + HCV_density + ">= " + percentage + " , 1)"
    HCV_kskog_expression = HCV_kskog_value_cores + " = if(" + HCV_kskog_density + ">= " + percentage + " , 1)"


    Module("g.message", message="\n \n" + HCV_expression + "\n \n")
    Module("g.message", message="\n \n" + HCV_kskog_expression + "\n \n")

    Module("r.mask", raster="NB_calc_nmd_gen@connectivity_forest_output", maskcats="3 51 52 62", flags="i")

    Module("r.mapcalc",
           expression=HCV_expression, overwrite=True)

    Module("r.mapcalc",
           expression=HCV_kskog_expression, overwrite=True)

    Module("r.mask", flags="r")

    Module("r.null", map=HCV_value_cores, setnull=0)
    Module("r.null", map=HCV_kskog_value_cores, setnull=0)

    Module("g.message", message="\n \n Save as vector \n \n")

    Module("r.to.vect",
           input=HCV_value_cores, output=HCV_value_cores, type="area", overwrite=True, flags="s")
    Module("r.to.vect",
           input=HCV_kskog_value_cores, output=HCV_kskog_value_cores, type="area", overwrite=True, flags = "s")

    # Compute areas and save as attributes

    Module("g.message", message="\n \n Computing areas \n \n")

    Module("v.to.db",
           map=HCV_value_cores, option="area", columns="area", overwrite=True)
    Module("v.to.db",
           map=HCV_kskog_value_cores, option="area", columns="area", overwrite=True)

    # Export shapefiles

    Module("g.message", message="\n \n Exporting shapefiles \n \n")

    Module("v.out.ogr", input=HCV_value_cores,
           output='/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Täthetsanalys/results/vardetrakter/' + HCV_value_cores + '.shp',
           format="ESRI_Shapefile", overwrite=True)
    Module("v.out.ogr", input=HCV_kskog_value_cores,
           output='/home/oskeng/Dropbox/Jobb/MIUN/Projekt/Konnektivitet_Norrbotten/Täthetsanalys/results/vardetrakter/' + HCV_kskog_value_cores + '.shp',
           format="ESRI_Shapefile", overwrite=True)



##################
# Uncomment what you want to run
#
tot_density(250)
#tot_density(500)
#tot_density(1000)

forest_density(250)
#forest_density(500)
#forest_density(1000)

vardetrakter('250','20')
vardetrakter('250','25')
vardetrakter('250','30')
vardetrakter('250','35')
vardetrakter('250','40')

# vardetrakter('500','25')
# vardetrakter('500','30')
# vardetrakter('500','35')
# vardetrakter('500','40')

# vardetrakter('1000','25')
# vardetrakter('1000','30')
# vardetrakter('1000','35')
# vardetrakter('1000','40')
