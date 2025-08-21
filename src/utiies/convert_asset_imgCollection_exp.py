#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
# SCRIPT DE CALCULO DE AREA DE AGUA POR GRIDS
# Produzido por Geodatin - Dados e Geoinformacao
# DISTRIBUIDO COM GPLv2
# Observações in https://code.earthengine.google.com/faff12027c2892a3fa261fc4183a0695
'''

import ee 
import os
import sys
import collections
collections.Callable = collections.abc.Callable
from pathlib import Path
pathparent = str(Path(os.getcwd()).parents[0])
print("pathparent ", pathparent)
# pathparent = str('/home/superuser/Dados/projAlertas/proj_alertas_ML/src')
sys.path.append(pathparent)
from configure_account_projects_ee import get_current_account, get_project_from_account
courrentAcc, projAccount = get_current_account()
print(f"projetos selecionado >>> {projAccount}  from {courrentAcc} <<<")
from gee_tools import *
try:
    ee.Initialize( project= projAccount )
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise
# sys.setrecursionlimit(1000000000)

def convert_month(numb):
    if numb < 10:
        return f"0{numb}"    
    return str(numb)

def exportarImagem(imgU, name_exp, geomet):    
    npath_asset = 'projects/mapbiomas-brazil/assets/WATER/COLLECTION-4/classification-monthly'
    IdAsset = os.path.join(npath_asset, name_exp)     
    optExp = {
        'image': imgU,
        'description': name_exp, 
        'assetId':IdAsset, 
        'pyramidingPolicy': {".default": "mode"},  
        'region': geomet, # .getInfo()['coordinates']
        'scale': 30,
        'maxPixels': 1e13 
    }

    task = ee.batch.Export.image.toAsset(**optExp)   
    task.start()

    print ("salvando ... ! " , name_exp)

year_inic = 1985
year_end = 2025
asset_water = 'projects/nexgenmap/TRANSVERSAIS/AGUA5-FT'
asset_limit = 'projects/mapbiomas-agua/assets/territories/countryPanAmazon'
geom_limit = ee.FeatureCollection(asset_limit).filter(ee.Filter.eq('name', 'Brasil')).geometry()
# Carrega a coleção original
colecaoBruta = (ee.ImageCollection(asset_water)
                    .filter(ee.Filter.eq('version', '11'))
                    .filter(ee.Filter.eq('cadence', 'monthly'))
        )

print('Total de imagens: ', colecaoBruta.size().getInfo())

# Lista de anos disponíveis
lst_years = list(range(year_inic, year_end + 1))
print('Anos disponíveis:   \n ', lst_years)

for cc, nyear in enumerate(lst_years[-1:]):
    print(f"# {cc}   processing year >> {nyear}")
    imagensDoAno = ee.Image(colecaoBruta.filter(ee.Filter.eq('year', nyear)).mosaic())

    for month in range(1, 13):        
        band_month = f"classification_{month}"
        string_month = convert_month(month)
        band_mes_f = f"water_monthly_{nyear}_{string_month}"       # "water_monthly_1985_05"      
        print("band mes F ", band_mes_f)  
        img_month = imagensDoAno.select(band_month).rename(band_mes_f)
        img_month = img_month.multiply(month)
        img_month = img_month.set(
            'module', 'Water',
            'submodule', 'Water',
            'variable', 'Water Monthly',
            'format', 'temporal_categorical_singleband_collection',
            'version', '1', 
            'year', nyear,
            'month', string_month,
            'system:footprint', geom_limit
        )
        # print("ver imagem ", img_month.getInfo())
        # sys.exit()

        exportarImagem(img_month, band_mes_f, geom_limit)
        # sys.exit()