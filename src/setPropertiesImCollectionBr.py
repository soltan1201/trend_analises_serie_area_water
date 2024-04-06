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
    'asset_input': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/grade_area_to_imColAL',
    'asset_centroi': 'projects/mapbiomas-arida/Mapbiomas/grids_attr_centroid',
    'asset_geom': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/geometry_grade',
    'asset_outputBR': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/stats_Kendall_cor',
    'asset_output': 'projects/nexgenmap/mosaic/stats_Kendall_AL',
    'regions': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    'asset_panAm': 'projects/mapbiomas-agua/assets/territories/countryPanAmazon',
    "calc_pValue": True,
    'year_start': 1985,
    'year_end': 2023    
}



lst_Code = ['2','5','6','7','8','9','4'] #  # '1','3',

dictCodPais = {
    '1': "Venezuela",
    '2': "Guyana",
    '3': "Colombia",
    '4': "Brasil",
    '5': "Ecuador",
    '6': "Suriname",
    '7': "Bolivia",
    '8': "Perú",
    '9': "Guyane Française"
}
dictCodPaisSig = {
    "ven": '1',
    "guy": '2',
    "col": '3',
    "bra": '4',
    "ecu": '5',
    "sur": '6',
    "bol": '7',
    "per": '8',
    "guf": '9'
}

 
lstMonths = [1,2,3,4,5,6,7,8,9,10,11,12];

lst_year = [kk for kk in range(param['year_start'], param['year_end'])]
contador = 1
window = len(lst_year)
total = len(lst_year)
print("==== SIZE WINDOWS INIT ===== ", window)

imgColTendc =  ee.ImageCollection(param['asset_outputBR'])
lstSystemIndexImg = imgColTendc.reduceColumns(ee.Reducer.toList(), ['system:index']).get('list').getInfo()
print(f"==== NEED TO SET PROPERTIES OF {len(lstSystemIndexImg)} IMAGE =======")
for cc, indiceSystem in enumerate(lstSystemIndexImg):
    print(cc , "========== processing code ==> ", indiceSystem);
    if cc > -1:   # 10378 # 20180
        # sys.exit()
        # mann_kendall_trend_test_watter_sazonal_cor_p_005_1985_2022
        partes = indiceSystem.split('_')      
        if "p_05_" in indiceSystem:  
            indP = '05'
        elif "p_025_" in indiceSystem:
            indP = '025'
        else:
            indP = '005'
        codeP = '4'
        nomePais = 'Brasil'
        intervalo = partes[-2] + '_' + partes[-1]
        
        print(indP, " ", codeP, " ", nomePais, " ", intervalo)


            
        assetIdImg = param['asset_outputBR'] + "/" + indiceSystem                     
        propiedadDict = {
            'p_value': indP,
            'code_country': codeP,
            'name_country': nomePais,            
            'interval': intervalo        
        }
        print(" ---- SET PROPERTY numberId to ---->  " + indiceSystem )
        ee.data.setAssetProperties(assetIdImg, propiedadDict)      
        

        
    






































