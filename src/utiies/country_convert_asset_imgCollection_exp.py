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

country_activo = 'peru'

dict_asset_input = {
    'bolivia': 'projects/mapbiomas-bolivia/assets/WATER/COLLECTION-3/01-SURFACE/E03-INTEGRATION/water-integracion-01',
    'ecuador': 'projects/mapbiomas-ecuador/assets/MAPBIOMAS-WATER/COLECCION3/ECUADOR/FINAL-ASSETS/water-surface-03',
    'peru': 'projects/mapbiomas-peru/assets/WATER/COLLECTION-3/FINAL-ASSETS/water-surface-01'
}

dict_asset_output = {
    'bolivia': 'projects/mapbiomas-bolivia/assets/WATER/COLLECTION-3/01-SURFACE/E03-INTEGRATION/water-monthly-01',
    'ecuador': 'projects/mapbiomas-ecuador/assets/MAPBIOMAS-WATER/COLECCION3/ECUADOR/FINAL-ASSETS/water-surface-monthly-03',
    'peru': 'projects/mapbiomas-peru/assets/WATER/COLLECTION-3/FINAL-ASSETS/water-monthly-01'
}

dict_monthly = {
    'peru': 'frequency',
    'bolivia': 'cadence'
}
dict_bands = {
    'peru': 'classification',
    'bolivia': 'w'
}

def convert_month(numb):
    if numb < 10:
        return f"0{numb}"    
    return str(numb)

def create_asset_path():
    asset_output = dict_asset_output[country_activo]
    properties = {
        'fonte': f'gt_water_{country_activo}',
        'data_criacao': '2025-09-13',
        'descricao': 'Este é um asset vazio, criado diretamente.'
    }
    # --- 1. Crie o asset container vazio ---
    # Use o método `ee.data.createAsset` para criar o container.
    # O parâmetro 'value' agora deve ser um dicionário que define o tipo de asset.
    # O parâmetro `force` é para sobrescrever.
    try:
        ee.data.createAsset(
            value={'type': 'ImageCollection',  'properties': properties}, # 
            path= asset_output,
            # force=False
        )
        print("building asset Image Collection in \n   >> " + asset_output)
        print("Este asset ainda não possui dados. Você precisa fazer a ingestão.")
    
    except Exception as e:
        print(f"Erro ao criar o asset: {e}")
        sys.exit()


def exportarImagem(imgU, name_exp, geomet):    
    npath_asset = dict_asset_output[country_activo]
    IdAsset = os.path.join(npath_asset, name_exp)     
    optExp = {
        'image': imgU,
        'description': name_exp, 
        'assetId':IdAsset, 
        'pyramidingPolicy': {".default": "mode"},  
        'region': ee.Geometry(geomet), # .getInfo()['coordinates']
        'scale': 30,
        'maxPixels': 1e13 
    }
\
    task = ee.batch.Export.image.toAsset(**optExp)   
    task.start()

    print ("salvando ... ! " , name_exp)


year_inic = 1985
year_end = 2025
create_asset = False
asset_water = dict_asset_input[country_activo]

if create_asset:
    create_asset_path()
    sys.exit()


# Carrega a coleção original
colecaoBruta = (ee.ImageCollection(asset_water)
                    .filter(ee.Filter.eq('version', 1))
                    .filter(ee.Filter.eq(dict_monthly[country_activo], 'monthly'))
        )

print('Total de imagens: ', colecaoBruta.size().getInfo())
geom_limit = ee.Geometry(colecaoBruta.first().geometry())
# sys.exit()
# Lista de anos disponíveis
lst_years = list(range(year_inic, year_end + 1))
print('Anos disponíveis:   \n ', lst_years)

for cc, nyear in enumerate(lst_years[1:]):
    print(f"# {cc}   processing year >> {nyear}")
    imagensDoAno = ee.Image(colecaoBruta.filter(ee.Filter.eq('year', nyear)).mosaic())

    for month in range(1, 13):        
        band_month = f"{dict_bands[country_activo]}_{month}"
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
            'month', string_month ,
            'system:footprint', geom_limit           
        )        
        # print("ver imagem ", img_month.getInfo())
        exportarImagem(img_month, band_mes_f, geom_limit)
        # sys.exit()