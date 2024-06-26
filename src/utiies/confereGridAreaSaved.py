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




params = {
    'assetBiomas': 'projects/mapbiomas-workspace/AUXILIAR/biomas_IBGE_250mil',
    'asset_grids': 'users/solkancengine17/shps_public/grid_5_5KM_AmericaL',
    'regions': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    'asset_input_br': 'projects/mapbiomas-workspace/TRANSVERSAIS/AGUA5-FT',
    'asset_gridBase': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/GRIDSTATS/GRIDBASE',
    'asset_asset_gradesArea': {'id': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/GRIDSTATS/version11_br'},
    'version': 11,

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
getsaved = True
knowSaved = {}
lst_Code = ['4'];  # '3','4','1','2','5','6','7','8','9' // 
lstreg = [
        '11','12','13','14','15','16','17','18','19',
        '21','22','23','24','31','32','35','34','33',
        '41','42','44','45','46','47','51','52','53',
        '60'
    ]
siglaCount = 'bra'
getlstGridAreas = ee.data.getList(params['asset_asset_gradesArea'])
print(f" we loaded  {len(getlstGridAreas)} features grades, we filtered by {siglaCount}")
print("the first ", getlstGridAreas[0])


for jj, idAsset in enumerate(getlstGridAreas):        
    path_ = idAsset.get('id')        
    lsFile =  path_.split("/")
    nameFile = lsFile[-1]
    partes = nameFile.split("_")
    nyear = partes[-1]
    region = partes[-2]
    # grids_attr_area_bra_ama_11_2009
    print(f" ======= loading region {region} year {nyear} ======")
    nkeys = [kk for kk in knowSaved.keys()]
    if region not in nkeys:
        knowSaved[region] = [nyear]

    else:
        lstYears = knowSaved[region]
        if nyear not in lstYears:
            lstYears.append(nyear)
            knowSaved[region] = lstYears
    
    
for kkey, lstValY in knowSaved.items():
    print(f"showing regions {kkey}  ===")
    lstFaltam = []
    for yyear in range(1985, 2024):
        if str(yyear) not in lstValY:
            lstFaltam.append(str(yyear))

    if len(lstFaltam) > 0:
        print(" === year que faltam =====\n ", lstFaltam) 
    else:
        print("------------------------------")
        print(f" === region {kkey} is complete ===")