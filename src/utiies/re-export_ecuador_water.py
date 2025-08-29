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

asset_water = 'projects/mapbiomas-ecuador/assets/MAPBIOMAS-WATER/COLECCION3/ECUADOR/FINAL-ASSETS/water-surface-03'

def exportarImagem(imgU, nameAl, mgeom):    
    IdAsset = asset_water + '/' + nameAl    
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


colecaoBruta = ee.ImageCollection(asset_water)
lst_idCod = colecaoBruta.reduceColumns(ee.Reducer.toList(), ['system:index']).get('list').getInfo()


for cc, idCod in enumerate(lst_idCod[:1]):
    print(f" #{cc}  >> {idCod}")
    img_raster = ee.Image(colecaoBruta.filter(ee.Filter.eq('system:index', idCod)).first())
    img_raster_proc = img_raster.gt(0).selfMask()
    img_raster_proc = img_raster_proc.copyProperties(img_raster, ['year', 'collection', 'cadence', 'source'])
    img_raster_proc = ee.Image(img_raster_proc).set(
                            'version', '2', 
                            'system:footprint', geomEc
                        )
    print(' bands >>> ', img_raster_proc.bandNames().getInfo())
    # print(img_raster_proc.getInfo()['properties'])
    # exportarImagem(img_raster_proc, idCod + '_v2', geomEc)

