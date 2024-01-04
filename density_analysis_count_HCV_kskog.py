#!/usr/bin/python3.11
#
# Computes r.neighbors for HCV forest (including continuity forest)
#
# Author: Oskar Englund
# Email: oskar.englund@miun.se
# Github: https://github.com/oskeng/konnektivitet_NB.git
#
######################
from typing import Any

import sys
import grass.script as gscript
from grass.pygrass.modules import Module
from grass.pygrass.modules.shortcuts import general as g
from grass.pygrass.modules.shortcuts import vector as v
from grass.pygrass.modules.shortcuts import raster as r

nmd_gen_study_area = 'nmd_gen_study_area@density_analysis'
input = 'out_input_HCV_kskog_final@HCV_kskog'
output_250 = 'output_HCV_kskog_250m_v2'
output_500 = 'output_HCV_kskog_500m_v2'
output_1000 = 'output_HCV_kskog_1000m_v2'

Module("g.region", raster=nmd_gen_study_area)

Module("g.message", message="\n \n Initiating r.neighbors for " + input + " and search radius 250m \n \n")

Module("r.neighbors", flags='c', overwrite=True, input=input,
       output=output_250, size=51, method='count', memory=30000)

Module("g.message", message="\n \n Initiating r.neighbors for " + input + " and search radius 500m \n \n")

Module("r.neighbors", flags='c', overwrite=True, input=input,
       output=output_500, size=101, method='count', memory=30000)

Module("g.message", message="\n \n Initiating r.neighbors for " + input + " and search radius 1000m \n \n")

Module("r.neighbors", flags='c', overwrite=True, input=input,
       output=output_1000, size=201, method='count', memory=30000)