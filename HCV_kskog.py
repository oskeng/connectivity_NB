#!/usr/bin/python3.11
#
# Identify HCV forest in Norrbotten county
#
# Author: Oskar Englund
# Email: oskar.englund@miun.se
# Github: https://github.com/oskeng/konnektivitet_NB.git
#
######################


from grass.pygrass.modules import Module

# input
nmd = 'nmd_gen_sv_updated@update_NMD'
national_parks = 'national_parks'
nature_reserves = 'nature_reserves'
protected_biotopes = 'protected_biotopes'
naturvardsavtal = 'naturvardsavtal'
N2000_ahd = 'N2000_ahd'
N2000_fd = 'N2000_fd'
key_biotopes = 'key_biotopes'
key_biotopes_ssb = 'key_biotopes_ssb'
value_cores = 'value_cores'
value_cores_rev = 'value_cores_rev'
kskog = 'kskog'

# calculated

value_cores_cross = 'calc_value_cores_cross'
value_cores_comb = 'calc_value_cores_comb'

# output

HCV = 'out_input_HCV'
HCV_forest = 'out_input_HCV_forest'
HCV_final = 'out_input_HCV_final'

HCV_kskog = 'out_input_HCV_kskog'
HCV_kskog_forest = 'out_input_HCV_kskog_forest'
HCV_kskog_final = 'out_input_HCV_kskog_final'

kskog_forest = 'out_input_kskog_forest'

#####

protected_val = '1'
value_cores_val = '2'
kskog_val = '3'

#####

Module("g.region", raster=nmd)

def message(message):

    Module("g.message", message="\n \n" + message + "\n \n", flags="w")

def rasterize():

    message("Rasterizing")
    Module("v.to.rast", input=national_parks, output=national_parks, use="val", memory="20000", overwrite=True)
    Module("v.to.rast", input=nature_reserves, output=nature_reserves, use="val", memory="20000", overwrite=True)
    Module("v.to.rast", input=protected_biotopes, output=protected_biotopes, use="val", memory="20000", overwrite=True)
    Module("v.to.rast", input=naturvardsavtal, output=naturvardsavtal, use="val", memory="20000", overwrite=True)
    Module("v.to.rast", input=N2000_fd, output=N2000_fd, use="val", memory="20000", overwrite=True)
    Module("v.to.rast", input=N2000_ahd, output=N2000_ahd, use="val", memory="20000", overwrite=True)
    Module("v.to.rast", input=key_biotopes, output=key_biotopes, use="val", memory="20000", overwrite=True)
    Module("v.to.rast", input=key_biotopes_ssb, output=key_biotopes_ssb, use="val", memory="20000", overwrite=True)
    Module("v.to.rast", input=value_cores, output=value_cores, use="val", memory="20000", overwrite=True)
    Module("v.to.rast", input=value_cores_rev, output=value_cores_rev, use="val", memory="20000", overwrite=True)

def identify_protected_land(value):

    message("Identifying protected land")

    Module("r.mapcalc", expression='calc_' + national_parks + " = if(" + nature_reserves + "," + value + ")",
           overwrite=True)
    Module("r.mapcalc", expression='calc_' + nature_reserves + " = if(" + nature_reserves + "," + value + ")",
           overwrite=True)
    Module("r.mapcalc", expression='calc_' + protected_biotopes + " = if(" + protected_biotopes + "," + value + ")",
           overwrite=True)
    Module("r.mapcalc", expression='calc_' + naturvardsavtal + " = if(" + naturvardsavtal + "," + value + ")",
           overwrite=True)
    Module("r.mapcalc", expression='calc_' + N2000_ahd + " = if(" + N2000_ahd + "," + value + ")",
           overwrite=True)
    Module("r.mapcalc", expression='calc_' + N2000_fd + " = if(" + N2000_fd + "," + value + ")",
           overwrite=True)

def identify_value_cores(value):

    message("Identifying value cores")

    # combine formal value cores with additions from LST

    Module("r.cross", input=value_cores + ',' + value_cores_rev, output=value_cores_cross, overwrite=True)

    # and assign the defined value

    Module("r.mapcalc", expression=value_cores_comb + " = if(" + value_cores_cross + "," + value + ")",
           overwrite=True)
    Module("r.mapcalc", expression='calc_' + key_biotopes + " = if(" + key_biotopes + "," + value + ")",
           overwrite=True)
    Module("r.mapcalc", expression='calc_' + key_biotopes_ssb + " = if(" + key_biotopes_ssb + "," + value + ")",
           overwrite=True)

def identify_kskog(value):

    message("Identifying continuity forest")

    Module("r.mapcalc", expression='calc_' + kskog + " = if(" + kskog + "," + value + ")",
           overwrite=True)

def combine():

    message("combining...")


    layers_HCV = 'calc_' + national_parks + ',calc_' + nature_reserves + ',calc_' + protected_biotopes + ',calc_' \
                     + naturvardsavtal + ',calc_' + N2000_fd + ',calc_' + N2000_ahd + ',' + value_cores_comb + ',calc_' \
                     + key_biotopes + ',calc_' + key_biotopes_ssb

    layers_HCV_kskog = layers_HCV + ',calc_' + kskog

    # combine all layers

    # Module("r.series", input=layers_HCV, output=HCV, method='minimum', overwrite=True)
    # Module("r.series", input=layers_HCV_kskog, output=HCV_kskog, method='minimum', overwrite=True)

    Module("r.null", map=HCV, null=0)
    Module("r.null", map=HCV_kskog, null=0)

    # exclude non-forest land (fellings are included since it is indeed forest land, just not currently forested)

    Module("r.mapcalc", expression = HCV_forest + "= if( " + nmd + "> 110, " + HCV + ", 0)", overwrite=True)
    Module("r.mapcalc", expression = HCV_kskog_forest + "= if( " + nmd + "> 110, " + HCV_kskog + ", 0)", overwrite=True)
    Module("r.mapcalc", expression= kskog_forest + "= if( " + nmd + "> 110, calc_" + kskog + ", 0)", overwrite=True)

    # finally, exclude temporary non-forest and recent fellings

    Module("r.mapcalc",
           expression=HCV_final + "= if( " + nmd + "!= 118 & " + nmd + " != 128 & " + nmd + " != 130, " + HCV_forest + ", 0)",
           overwrite=True)
    Module("r.mapcalc",
           expression=HCV_kskog_final + "= if( " + nmd + "!= 118 & " + nmd + " != 128 & " + nmd + " != 130, " + HCV_kskog_forest + ", 0)",
           overwrite=True)

    Module("r.null", map=HCV_final, setnull=0)
    Module("r.null", map=HCV_kskog_final, setnull=0)



#####################
# uncomment to run #
#
#
#rasterize()
#identify_protected_land(protected_val)
#identify_value_cores(value_cores_val)
#identify_kskog(kskog_val)
#combine()