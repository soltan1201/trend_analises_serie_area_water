#!/usr/bin/env python2
# -*- coding: utf-8 -*-

##########################################################
## CRIPT DE EXPORTAÇÃO DO RESULTADO FINAL PARA O ASSET  ##
## DE mAPBIOMAS                                         ##
## Produzido por Geodatin - Dados e Geoinformação       ##
##  DISTRIBUIDO COM GPLv2                               ##
#########################################################

import ee 
import gee
import json
import csv
import sys
from icecream import ic
import pandas as pd

try:
    ee.Initialize()
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


param = {
    'asset_asset_gradesArea': {'id': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/GRIDSTATS/versionPanAm_4'},
    'asset_centroi': 'projects/mapbiomas-arida/Mapbiomas/grids_attr_centroid',
    'asset_output': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/grade_area_to_imColAL/',
    # 'asset_geom': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/geometry_grade',
    'asset_panAm': 'projects/mapbiomas-agua/assets/territories/countryPanAmazon',
    'asset_grids': 'users/solkancengine17/shps_public/grid_5_5KM_AmericaL',
    'regions': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    'asset_gridBase': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/GRIDSTATS/GRIDBASE',
    'numeroTask': 1,
    'numeroLimit': 40,
    'conta' : {
        '0': 'caatinga01',
        '8': 'caatinga02',
        '16': 'caatinga03',
        '24': 'caatinga04',
        '32': 'caatinga05'       
    }
}
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
dictNameCountry = {
    "ven": "Venezuela",
    "guy": "Guyana",
    "col": "Colombia",
    "bra": "Brasil",
    "ecu": "Ecuador",
    "sur": "Suriname",
    "bol": "Bolivia",
    "per": "Perú",
    "guf": "Guyane Française"
}
dictNametoCode = {
    "ven": "1",
    "guy": "2",
    "col": "3",
    "bra": "4",
    "ecu": "5",
    "sur": "6",
    "bol": "7",
    "per": "8",
    "guf": "9"
}
dictRegions = {
    '11': 'AMAZONIA',
    '12': 'AMAZONIA',
    '13': 'AMAZONIA',
    '14': 'AMAZONIA',
    '15': 'AMAZONIA',
    '16': 'AMAZONIA',
    '17': 'AMAZONIA',
    '18': 'AMAZONIA',
    '19': 'AMAZONIA',
    '21': 'CAATINGA',
    '22': 'CAATINGA',
    '23': 'CAATINGA',
    '24': 'CAATINGA',
    '31': "CERRADO",
    '32': "CERRADO",
    '35': "CERRADO",
    '34': "CERRADO",
    '33': "CERRADO",
    '41': "MATAATLANTICA",
    '42': "MATAATLANTICA",
    '44': "MATAATLANTICA",
    '45': "MATAATLANTICA",
    '46': "MATAATLANTICA",
    '47': "MATAATLANTICA",
    '51': "PAMPA",
    '52': "PAMPA",
    '53': "PAMPA",
    '60': "PANTANAL"   
}

dictRegSigla = {
    '11': 'ama',
    '12': 'ama',
    '13': 'ama',
    '14': 'ama',
    '15': 'ama',
    '16': 'ama',
    '17': 'ama',
    '18': 'ama',
    '19': 'ama',
    '21': 'caa',
    '22': 'caa',
    '23': 'caa',
    '24': 'caa',
    '31': "cer",
    '32': "cer",
    '35': "cer",
    '34': "cer",
    '33': "cer",
    '41': "mat",
    '42': "mat",
    '44': "mat",
    '45': "mat",
    '46': "mat",
    '47': "mat",
    '51': "pam",
    '52': "pam",
    '53': "pam",
    '60': "pan"   
}
#========================METODOS=============================
def gerenciador(cont, paramet):
    #0, 18, 36, 54]
    #=====================================
    # gerenciador de contas para controlar 
    # processos task no gee
    # cada conta vai rodar com 18 cartas X 3 anos
    #=====================================
    numberofChange = [kk for kk in paramet['conta'].keys()]
    
    if str(cont) in numberofChange:

        print("conta ativa >> {} <<".format(paramet['conta'][str(cont)]))        
        gee.switch_user(paramet['conta'][str(cont)])
        gee.init()        
        gee.tasks(n= paramet['numeroTask'], return_list= True)        
    
    elif cont > paramet['numeroLimit']:
        cont = 0
        return cont
    
    cont += 1    
    return cont

def exportarImagem(imgU, nameAl, geomet):
    
    IdAsset = param['asset_output'] + nameAl   
    
    optExp = {
        'image': imgU,
        'description': nameAl, 
        'assetId':IdAsset, 
        'pyramidingPolicy': {".default": "mode"},  
        'region': geomet, # .getInfo()['coordinates']
        'scale': 5000,
        'maxPixels': 1e13 
    }

    task = ee.batch.Export.image.toAsset(**optExp)   
    task.start()


    # for keys, vals in dict(task.status()).items():
    #     print ( "  {} : {}".format(keys, vals))
    
    print ("salvando ... ! " , nameAl)

def GetPolygonsfromFolder(siglaCount):
    
    dictSigPais = {
        'ven': '1',
        'col': '3',
        'bra': '4'
    }
    siglaCount = 'grids_attr_area_' + siglaCount
    print(f' sigla now is ===> {siglaCount} < ===')
    regionsBr = ee.FeatureCollection(param['regions']);
    countryAmazonia = ee.FeatureCollection(param['asset_panAm'])
    lsfaltantes = []
    code_region = None
    name_biome = None
    sigla_biome = None
    # processar = False
    getlistPtos = ee.data.getList(param['asset_asset_gradesArea'])
    print(f" we loaded {len(getlistPtos)} features grades ")
    # img_col_grades = ee.List([])
    allBands = []
    ls_col_final = []
    ls_name_col = ['area_' +  str(kk) for kk in range(1, 13)]
    # ls_name_col = ls_name_col + ['area_annual']
    allBands += ls_name_col
    primeiro_ano = 1985
    
    contAuth = 0
    # contador = 1
    for jj, idAsset in enumerate(getlistPtos):        
        
        path_ = idAsset.get('id')        
        lsFile =  path_.split("/")
        nameFile = lsFile[-1]
        # lst_name = ['grids_attr_2022'] # , 'grids_attr_2021', 'grids_attr_2022'
        # if name in lst_name:
        # ===== PROCESSING grids_bra_ama_11_2017 =====
        # grids_attr_area_bra_ama_13_2023       

        if  jj > -1 and siglaCount in nameFile:
            print(f"===== {jj} PROCESSING {nameFile} =====")  
            partes = nameFile.split("_")
            feat_tp = ee.FeatureCollection(path_)    
            myear = int(partes[-1])
            code_country = dictNametoCode[partes[3]]
            name_country = dictNameCountry[partes[3]]

            if siglaCount == 'grids_attr_area_bra':
                code_region = partes[-2]
                name_biome = dictRegions[code_region]
                sigla_biome = dictRegSigla[code_region]
                print("year = ", myear, 'codigo do pais = ', code_country, " name country = ", name_country,
                            " sigla biome = ", sigla_biome, " code region = ", code_region, " name biome = ", name_biome)            
            else:
                print("year = ", myear, 'codigo do pais = ', code_country, " name country = ", name_country)           
            
            
            PageName = feat_tp.first().get('PageName').getInfo()
            PageNumber = feat_tp.first().get('PageNumber').getInfo()
            # code_country = feat_tp.first().get('code_country').getInfo()
            
            if 'grids_bra' in nameFile:
                code_region = feat_tp.first().get('code_region').getInfo()
                name_biome = feat_tp.first().get('name_biome').getInfo()              
                    

            # geometry of image 
            if str(code_country) == '4': 
                geomet = regionsBr.filter(
                                ee.Filter.eq('region', int(code_region))
                            )
            else:
                geomet = countryAmazonia.filter(
                            ee.Filter.eq('code', int(code_country)))        
            
            geomet = geomet.geometry()
            ic(" GEOMETRY REGIONS ", geomet.getInfo().keys())


            ic(f"mostrando as propiedades do ano {myear} para {name_country}" )
            ic(feat_tp.first().propertyNames().getInfo()) # ['properties']
            
            for cc, banda in enumerate(ls_name_col):

                numb_bnd = banda.replace('area_', '')
                numb_bnd = int(numb_bnd)

                difYear = myear - primeiro_ano
                numbMonth = (difYear * 12) + numb_bnd
                # banda do mes numerado 
                bandaMonthNum = 'area_' + str(numbMonth)
                ls_col_final.append(bandaMonthNum)
                # print(numb_bnd)
                # if cc > 2:
                #     sys.exit()
                if numb_bnd not in lsfaltantes:
                    print(" imagem " + banda + " => correspondente a ", bandaMonthNum, " => ", name_country)

                    img_feat = feat_tp.reduceToImage(properties= [banda], reducer= ee.Reducer.first())   
                    img_feat = img_feat.unmask(0).rename('area')
                    
                    if (cc + 1) < 10:
                        dat_year = str(myear) + '-' + '0' + str(cc + 1) + '-01'
                    else: 
                        dat_year = str(myear) + '-' + str(cc + 1) + '-01'
                    
                    nameBnb = nameFile.replace('grids_', '')
                    nameBnb = nameBnb.replace('attr_', '')
                    nameBnb = nameBnb + '_' + banda

                    img_feat = img_feat.set(
                                    'system:time_start', ee.Date(dat_year),
                                    'system:index', nameBnb,
                                    'system:footprint', geomet,
                                    'numId', numbMonth,
                                    'name_country', name_country,
                                    'code_country', code_country,
                                    'PageName', PageName,
                                    'PageNumber', PageNumber,
                                    'code_region', code_region,
                                    'name_biome', name_biome
                                )


                    exportarImagem(img_feat, nameBnb, geomet)
                    # img_col_grades = img_col_grades.add(img_feat)
                    # contAuth = gerenciador(contAuth, param)
            # contador += 1
    # if jj > 50:
    #     sys.exit()

    # return  ee.ImageCollection(img_col_grades)

if  __name__ == "__main__":
    siglaPais = 'bra'
    GetPolygonsfromFolder(siglaPais)
