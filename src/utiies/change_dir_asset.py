#-*- coding utf-8 -*-
import ee
import os
import sys

import collections
from pathlib import Path
collections.Callable = collections.abc.Callable

pathparent = str(Path(os.getcwd()).parents[0])
sys.path.append(pathparent)
from configure_account_projects_ee import get_current_account, get_project_from_account
projAccount = get_current_account()
print(f"projetos selecionado >>> {projAccount} <<<")

try:
    ee.Initialize(project= projAccount[1]) # project='ee-cartassol'
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise

def sendFilenewAsset(idSource, idTarget):
    # moving file from repository Arida to Nextgenmap
    ee.data.renameAsset(idSource, idTarget)

asset_water = 'projects/mapbiomas-ecuador/assets/MAPBIOMAS-WATER/COLECCION3/ECUADOR/FINAL-ASSETS/water-surface-03'
asset_water_base = 'projects/mapbiomas-ecuador/assets/MAPBIOMAS-WATER/COLECCION3/ECUADOR/FINAL-ASSETS'

# imgCol = ee.ImageCollection(asset_water_base)
lstIdsfails = []

for nyear in range(1985, 2025):
    print(f" processing year {nyear}")
    name_img_yy = f'water-{nyear}_annual_v2'
    try:        
        asset_input = asset_water + name_img_yy
        # ee.data.deleteAsset(asset_input)
        print("deleting image >> " + asset_input)
    except:
        print(f" ---- raster {name_img_yy} fails ----- ")
        lstIdsfails.append(name_img_yy)

    name_img_mm = f'water-{nyear}_mensual_v2'
    try:
        asset_inputMM = asset_water + name_img_mm
        # ee.data.deleteAsset(asset_inputMM)
        print("deleting image >> " + asset_inputMM)
    except:
        print(f" ---- ratser {name_img_mm} fails ----- ")
        lstIdsfails.append(name_img_mm)
    
    

        
        
print(lstIdsfails)