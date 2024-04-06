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
    'asset_input': 'projects/nexgenmap/mosaic/stats_Kendall_AL',
    'asset_inputBr': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/stats_Kendall_cor',    
    'asset_geom': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/geometry_grade',
    'asset_output': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/stats_Kendall_AL',
    # 'asset_panAm': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/limitPanAmazon',
    'asset_panAm': 'projects/mapbiomas-agua/assets/territories/countryPanAmazon',
    "calc_pValue": True,
    'year_start': 1985,
    'year_end': 2023,
    'numeroTask': 3,
    'numeroLimit': 100,
    'conta' : {
        '0': 'caatinga01',
        '10': 'caatinga02',
        '20': 'caatinga03',
        '30': 'caatinga04',
        '40': 'caatinga05',
        '50': 'solkan1201',   #      
        '60': 'diegoGmail',  
        '70': 'superconta'    
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
        
# agrupando todas as combinações aqui 
lista_Windows_years = []
while window > 4:
    diff = total - window
    if diff == 0:
        # print("{} : windows {} : {} ".format(contador, window, lst_year))
        lista_Windows_years.append(lst_year)
        contador += 1
    
    else:
        for ii in range(diff + 1):
            print("{} : windows {} : {} ".format(contador, window, lst_year[ii: window + ii]))
            lista_Windows_years.append(lst_year[ii: window + ii])
            contador += 1
    
    window -= 1

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

print(f"--- the list of years windows have {len(lista_Windows_years)} lists --- ")
# sys.exit()
lst_Code = ['1','2','3','4','6','7','8','9'];  # '5', # '2','4'==>  '2','6','7','8','9',
lst_codeNotBr =  ['1','2','3','5','6','7','8','9'];
# lst_Code = ['6','7'];

lst_indP = ['005', '05']

limit_paises = ee.FeatureCollection(param['asset_panAm']).geometry()              

imgCol = ee.ImageCollection(param['asset_input']).filter(
                                    ee.Filter.inList('code_country', lst_codeNotBr)).merge(
                                        ee.ImageCollection(param['asset_inputBr']))

cont = 0
cont = gerenciador(cont, param)
for cc, wls_year in enumerate(lista_Windows_years[4:]): 
    
    year_start = wls_year[0]
    year_end = wls_year[-1]
    intervalo = str(year_start) + "_" + str(year_end)
    lst_indexSys = []
    for indP in lst_indP:               
    
        # print(" número de index imagens ", len(lst_indexSys))
        imgUnion = imgCol.filter(
                        ee.Filter.eq('p_value', indP)).filter(
                            ee.Filter.eq('interval', intervalo))
        
        size_lstIm = imgUnion.size().getInfo()
        print('número de imagens ', size_lstIm)
        # mann_kendall_trend_test_watter_sazonal_cor_p_025_1985_2022
        sufixo = 'mann_kendall_trend_test_watter_sazonal_cor_p_'
        nameAl = sufixo + indP + "_" +  intervalo
        print(cc, " => ", nameAl)
        # sys.exit()
        if size_lstIm == 9:
            print(" este link pode salvar ")
            
        else:
            # print(" " + nameAl)
            
            print(f" Faltam {9 - size_lstIm} imagens ")
            lstIds = imgUnion.reduceColumns(ee.Reducer.toList(), ['system:index']).get('list').getInfo()
            for idd in lstIds:
                print("    ", idd)
        
        imgUnion = imgUnion.mosaic()
        imgUnion = imgUnion.set( 
                    'p_value', indP,
                    'interval', intervalo
                )
        exportarImagem(imgUnion, nameAl, limit_paises)    
        cont = gerenciador(cont, param)