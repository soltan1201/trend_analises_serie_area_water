#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
# SCRIPT DE CALCULO DE AREA DE AGUA POR GRIDS
# Produzido por Geodatin - Dados e Geoinformacao
# DISTRIBUIDO COM GPLv2
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

lstCoord = [
    [-82.31406366826762,-5.229503725077616],
    [-74.77744257451762,-5.229503725077616], 
    [-74.77744257451762,2.013782132467362],
    [-82.31406366826762,2.013782132467362],
    [-82.31406366826762,-5.229503725077616]
]
geomEc = ee.Geometry.Polygon(lstCoord)
create_asset = True
asset_water = 'projects/mapbiomas-ecuador/assets/MAPBIOMAS-WATER/COLECCION3/ECUADOR/FINAL-ASSETS/clasificacion-glaciar-EC_C3'
asset_output = 'projects/mapbiomas-ecuador/assets/MAPBIOMAS-WATER/COLECCION3/ECUADOR/FINAL-ASSETS/collection-glaciar-EC_C3'

if create_asset:    
    properties = {
        'fonte': 'gt_Glaciar_ecuador',
        'data_criacao': '2025-08-25',
        'descricao': 'Este é um asset vazio, criado diretamente.'
    }
    # --- 1. Crie o asset container vazio ---
    # Use o método `ee.data.createAsset` para criar o container.
    # O parâmetro 'value' agora deve ser um dicionário que define o tipo de asset.
    # O parâmetro `force` é para sobrescrever.
    try:
        ee.data.createAsset(
            value={'type': 'ImageCollection',  'properties': properties}, # 
            path=asset_output,
            # force=False
        )
        print("building asset Image Collection in \n   >> " + asset_output)
        print("Este asset ainda não possui dados. Você precisa fazer a ingestão.")
    except Exception as e:
        print(f"Erro ao criar o asset: {e}")
        create_asset = False
    

def exportarImagem(imgU, nameAl, mgeom):    
    IdAsset = os.path.join(asset_output, nameAl)  
    optExp = {
        'image': imgU,
        'description': nameAl, 
        'assetId':IdAsset, 
        'pyramidingPolicy': {".default": "mode"},  
        'region': mgeom, # .getInfo()['coordinates']
        'scale': 30,
        'maxPixels': 1e13 
    }

    task = ee.batch.Export.image.toAsset(**optExp)   
    task.start()
    
    print ("salvando ... ! " , nameAl)


raster_bruto = ee.Image(asset_water)
year_end = 2024

if create_asset:
    for cc, nyear in enumerate(range(1985, year_end + 1)):
        print(f" #{cc}  >> {nyear}")
        img_raster_yy = raster_bruto.select(f"classification_{nyear}")
        img_raster_yy = img_raster_yy.gt(0).selfMask()    
        img_raster_yy = ee.Image(img_raster_yy).set(
                                'version', '1', 'year', nyear,
                                'cadence','annual', 'code_region', 1004,
                                'collection', '3', 'descripcion', 'filtro espacial',
                                'pais', 'ECUADOR', 'paso', 'P03',
                                'source', 'gtglaciar', 'system:footprint', geomEc
                            )

        # print(' bands >>> ', img_raster_yy.bandNames().getInfo())
        name_export = f"glaciar-{nyear}_annual_v1"
        exportarImagem(img_raster_yy, name_export, geomEc)

