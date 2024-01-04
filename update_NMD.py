#!/usr/bin/python3.11
#
# Updates the land use map to function as input data to the other scripts
#
# Author: Oskar Englund
# Email: oskar.englund@miun.se
# Github: https://github.com/oskeng/konnektivitet_NB.git
#
######################
from typing import Any

from grass.pygrass.modules import Module

# input data
input_nmd = 'nmd_gen_sv@update_NMD'
power_lines = 'power_lines@update_NMD'
fellings = 'fellings_231002@update_NMD'

# calculated
power_line_buffer = 'power_lines_buffer@update_NMD'
recent_fellings = 'recent_fellings_231002@update_NMD'

# output data
output_nmd = 'nmd_gen_sv_updated@update_NMD'

Module("g.region", raster=input_nmd)

#####
print("\n \n updating NMD with transmission lines \n \n ")

Module("v.db.addcolumn", map=power_lines, columns="buffer int")

Module("v.db.update", map=power_lines, column="buffer", value="50", where="objekttyp = 'Kraftledning stam'")
Module("v.db.update", map=power_lines, column="buffer", value="25", where="objekttyp = 'Kraftledning region'")
Module("v.db.update", map=power_lines, column="buffer", value="5", where="objekttyp = 'Kraftledning fördelning'")

Module("v.buffer", input=power_lines, layer="1", output=power_line_buffer, column="buffer", overwrite=True)

Module("v.to.rast", input=power_line_buffer, type='area', output=power_line_buffer, use="val", value="1", memory="50000", overwrite=True)

Module("r.null",
       map=power_line_buffer, null=0)

# Transmission lines are given value 54

Module("r.mapcalc",
       expression=output_nmd + " = if( " + power_line_buffer + " == 1, 54, " + input_nmd + ")", overwrite=True)

#####
print("\n \n updating NMD with recent fellings \n \n")

Module("v.db.addcolumn", map=fellings, columns="avvyear int")

Module("v.db.update", map=fellings, column="avvyear", query_column="substr(Avvdatum,1,4)")

Module("v.extract", input=fellings, type="area", where="avvyear > 2018", output=recent_fellings, overwrite=True)

Module("v.to.rast", input=recent_fellings, layer="1", type="area", output=recent_fellings, use="val", value="1", memory="50000", overwrite=True)

Module("r.null", map=recent_fellings, null=0)

# Recent fellings are given value 130

Module("r.mapcalc", expression=output_nmd + " = if( " + recent_fellings + " == 1, 130, " + output_nmd + ")", overwrite=True)

#####
print("\n \n retaining water and urban land \n \n")

Module("r.mapcalc", expression=output_nmd + " = if( " + input_nmd + " == 61 | " + input_nmd + " == 62 | " + input_nmd + " == 51 | " + input_nmd + " == 52 | " + input_nmd + " == 53, " + input_nmd + ", " + output_nmd + ")", overwrite=True)