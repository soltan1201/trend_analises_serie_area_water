#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##########################################################
## CRIPT DE EXPORTAÇÃO DO RESULTADO FINAL PARA O ASSET  ##
## DE mAPBIOMAS                                         ##
## Produzido por Geodatin - Dados e Geoinformação       ##
##  DISTRIBUIDO COM GPLv2                               ##
#########################################################
# https://developers.google.com/earth-engine/tutorials/community/nonparametric-trends

import ee 
import gee
import json
import csv
import sys
import copy
from datetime import date
try:
    ee.Initialize()
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


param = {
    'asset_inputBR': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/harmonic_imCol_area',    
    'asset_geom': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/geometry_grade',
    'asset_output': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/harmonic_imCol_areaAL',
    'asset_input': 'projects/nexgenmap/mosaic/harmonic_imCol_area_AL',
    'asset_panAm': 'projects/mapbiomas-agua/assets/territories/countryPanAmazon',
    "calc_pValue": True,
    'year_start': 1985,
    'year_end': 2023,
    'numeroTask': 3,
    'numeroLimit': 200,
    'conta' : {
        '0': 'caatinga01',
        '20': 'caatinga02',
        '40': 'caatinga03',
        '60': 'caatinga04',
        '80': 'caatinga05',
        '100': 'solkan1201',   #      
        '120': 'diegoGmail',  
        '140': 'superconta'    
    },
    
}
def gerenciador(cont, paramet):    
    #0, 18, 36, 54]
    #=====================================#
    # gerenciador de contas para controlar# 
    # processos task no gee               #
    #=====================================#
    numberofChange = [kk for kk in paramet['conta'].keys()]    
    if str(cont) in numberofChange:

        print("conta ativa >> {} <<".format(paramet['conta'][str(cont)]))        
        gee.switch_user(paramet['conta'][str(cont)])
        gee.init()        
        gee.tasks(n= paramet['numeroTask'], return_list= True)        
    
    elif cont > paramet['numeroLimit']:
        cont = 0    
    cont += 1    
    return cont

def exportarImagem(imgU, nameAl, geomet):    
        
        IdAsset = param['asset_output'] + '/' + nameAl   
        
        optExp = {
            'image': imgU,
            'description': nameAl, 
            'assetId':IdAsset, 
            'pyramidingPolicy': {".default": "mode"},  
            'region': geomet, #.getInfo()['coordinates'],
            'scale': 5000,
            'maxPixels': 1e13 
        }

        task = ee.batch.Export.image.toAsset(**optExp)   
        task.start()
        
        print (f"salvando ... {nameAl} !")
        

lst_year = [kk for kk in range(param['year_start'], param['year_end'])]
contador = 1
window = len(lst_year)
total = len(lst_year)
print("==== SIZE WINDOWS INIT ===== ", window)

dictCodPaisSig = {
        '1': "ven",
        '2': "guy",
        '3': "col",
        '4': "bra",
        '5': "ecu",
        '6': "sur",
        '7': "bol",
        '8': "per",
        '9': "guf"
    }

lst_Code = ['1','2','3','4','6','7','8','9'];  # '5', # '2','4'==>  '2','6','7','8','9',
lst_codeNotBr =  ['1','2','3','5','6','7','8','9'];

limit_paises = ee.FeatureCollection(param['asset_panAm']).geometry()  
imgCol = ee.ImageCollection(param['asset_input']).merge(
                                        ee.ImageCollection(param['asset_inputBR']))

cont = 0
cont = gerenciador(cont, param)
for cc, cyear in enumerate(lst_year[:]):
    for mes in range(1, 13):
        numbId =  (cyear - 1985) * 12 + mes    
        
        imgUnion = imgCol.filter(
                        ee.Filter.eq('numId', numbId))                            
        
        size_lstIm = imgUnion.size().getInfo()
        print(f" número de index  {numbId} com {size_lstIm} de imagens")
        
        # mann_kendall_trend_test_watter_sazonal_cor_p_025_1985_2022        
        nameAl = "area_harmonic_" + str(numbId)
        print(cc, " => ", nameAl)
        # sys.exit()

        imgUnion = imgUnion.mosaic()
        imgUnion = imgUnion.set( 
                    'numId', numbId                    
                )
        exportarImagem(imgUnion, nameAl, limit_paises)    
        cont = gerenciador(cont, param)