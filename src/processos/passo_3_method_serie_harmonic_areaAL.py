#!/usr/bin/env python2
# -*- coding: utf-8 -*-

##########################################################
## CRIPT DE EXPORTAÇÃO DO RESULTADO FINAL PARA O ASSET  ##
## DE mAPBIOMAS                                         ##
## Produzido por Geodatin - Dados e Geoinformação       ##
##  DISTRIBUIDO COM GPLv2                               ##
#########################################################

import ee 
import os
import sys

import numpy as np
from datetime import date
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


param = {
    # 'asset_input': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/grade_area_to_imColAL',
    # 'asset_inputBR': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/grade_area_to_imCol',
    'asset_input': 'projects/nexgenmap/GTAGUA/grade_area_to_imColrbr',
    'asset_centroi': 'projects/mapbiomas-arida/Mapbiomas/grids_attr_centroid',
    # 'asset_output': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/MOSAIC/harmonic_imCol_areaBR',
    'asset_output': 'projects/nexgenmap/GTAGUA/harmonic_imCol_areaBR',
    'asset_panAm': 'projects/mapbiomas-agua/assets/territories/countryPanAmazon',
    'regionsBr': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    'numeroTask': 1,
    'numeroLimit': 8,
    'date_inic': 1985,
    'date_end': 2024,
    'conta' : {
        '0': 'caatinga01',        
        '1': 'caatinga02',
        '2': 'caatinga03',
        '3': 'caatinga04',
        '4': 'caatinga05',
        '5': 'solkan1201',   #      
        # '6': 'solkanGeodatin',
        '6': 'superconta' 
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
contAuth = 0
class calculo_harmonic(object):

    # contador = 1
    def __init__(self, matrix_coef, geometria, asset_output):

        self.array_Trend_Coef = matrix_coef
        self.geomet = geometria
        self.output = asset_output
    
    def estimate_harmonic_area(self, img):
        
        v_dependent = 'area'
        v_independent = ['constant', 't', 'cos', 'sin']

        img_temp = img.select(v_independent).multiply(  
                            self.array_Trend_Coef).reduce('sum').rename('area_harmonic')
        
        # nameAl = 'area_harmonic_' + str(self.contador)
        
        # self.exportarImagem(img.select(v_dependent).addBands(img_temp), nameAl)
        # self.contador += 1

        return img.select(v_dependent).addBands(img_temp)


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
        switch_user(paramet['conta'][str(cont)])
        try:
            ee.Initialize(project= projAccount) # project='ee-cartassol'
            print('The Earth Engine package initialized successfully!')
        except ee.EEException as e:
            print('The Earth Engine package failed to initialize!')      
        tarefas = tasks(n= paramet['numeroTask'], return_list= True, print_tasks= False)    
        for cc, lin in enumerate(tarefas):            
            # relatorios.write(str(lin) + '\n')
            print(cc, lin)          
    
    elif cont > paramet['numeroLimit']:
        return 0
    
    cont += 1    
    return cont

def exportarImagem(imgU, nameAl, geomet):    
        
        IdAsset =  param['asset_output'] + "/" + nameAl        
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
        print ("salvando imagem {} !!!!".format(nameAl))

def get_number_ids(img):

    numid = img.get('numId')
    # numid = ee.String(numid).replace('area_', '')
    numid = ee.Number(numid).int16()
    val_yy = numid.divide(12).floor().add(1985)     
    cc = numid.add(1).mod(12)
    cc = ee.Algorithms.If(ee.Algorithms.IsEqual(
                                ee.Number(cc).eq(0), 1), ee.Number(12), cc )

    dat_year = ee.Date.fromYMD(val_yy, cc, 1)
    return img.rename(['area']).set('numId', numid, 'system:start', dat_year)

def addVariables_tempo(image):
    # Compute time in fractional years since the epoch.
    date = ee.Date(image.get('system:start'))
    years = date.difference(ee.Date('1985-01-01'), 'year')

    timeRadians = ee.Image(years).multiply(2 * np.pi)

    return image.select(['area']).float().addBands(
                ee.Image(years).rename('t').float()).addBands(
                    timeRadians.cos().rename('cos')).addBands(
                        timeRadians.sin().rename('sin')).addBands(
                            ee.Image.constant(1))

def building_Harmonic_time_serie(tmpImgCol, codeP, iDregion, geomet):
    geomet = ee.Geometry(geomet)
    # var_dependent = 'area'
    var_independent = ['constant', 't', 'cos', 'sin']
    all_variables = ['constant', 't', 'cos', 'sin', 'area']

    img_col_addTemp = tmpImgCol.map(lambda img: addVariables_tempo(img));
    print("show bands ", img_col_addTemp.first().bandNames().getInfo());
    # calculando os coeficientes de cada imagem 
    # The output of the regression reduction is a 4x1 array image area.
    harmonicTrend_coef = img_col_addTemp.select(all_variables).reduce(
                        ee.Reducer.linearRegression(len(var_independent), 1))


    # Turn the array image into a multi-band image of coefficients .
    array_Trend_Coef = harmonicTrend_coef.select('coefficients') \
                                        .arrayProject([0]) \
                                        .arrayFlatten([var_independent])

    # Compute fitted values
    # calculo_harmonico = calculo_harmonic(array_Trend_Coef, geomet, param['asset_output'])
    # fittedHarmonicM = img_col_addTemp.map(lambda img : calculo_harmonico.estimate_harmonic_area(img))

    fittedHarmonicM = img_col_addTemp.map(lambda img : img.addBands(img.select(var_independent).multiply(  
                                array_Trend_Coef).reduce('sum').rename('area_harmonic')))

    fittedHarmonicM = fittedHarmonicM.select(['area', 'area_harmonic'])
    print(fittedHarmonicM.first().bandNames().getInfo())
    # print(fittedHarmonicM.first().get('system:index').getInfo())
    sizeSerie = (param['date_end'] - param['date_inic'] + 1) * 12 + 1
    print(F"***** WE WILL ESTIMATE {sizeSerie} IMAGE HARMONIC **************")
    for ii in range(1, sizeSerie):
        print("processando a imagem # {} ".format(ii))
        
        img_band = 'area_' + str(ii)
        img_tmp =  fittedHarmonicM.filter(ee.Filter.eq('numId', ii)).first()
        
        img_tmp = img_tmp.set('system:index', img_band)
        # img_tmp = img_tmp.clip(geomet).set('system:footprint', geomet)
        img_tmp = img_tmp.set('numId', ii)
        img_tmp = img_tmp.set('code_country', codeP)
        img_tmp = img_tmp.set('code_region', iDregion)

        if iDregion != "":
            name_im = 'area_harmonic_' + dictCodPaisSig[codeP] + "_" + iDregion  + "_" + str(ii)
        else:
            name_im = 'area_harmonic_' + dictCodPaisSig[codeP] + "_" + str(ii)
            print(name_im)
        # if ii > sizeSerie - 25:
        exportarImagem(img_tmp, name_im, geomet)
        # sys.exit() 
    

# contAuth = gerenciador(6, param)
lst_Code = ['8'];  # '1','2','3','4','5','6','7','8','9'
lstCodeReg =  [
        '11','12','13','14','15','16',
        '17','18','19','21','22',
        '23','24',
        '31','32','35','34',
        '33','41','42',
        '44','45',
        '46','47','51','52','53','60'               
    ]
# code_country
imC_areaCountry = ee.ImageCollection(param['asset_input']).filter(
                        ee.Filter.inList('code_country', lst_Code))
# imgCol_areaBr = ee.ImageCollection(param['asset_input'])
print(f"=== we loaded {imC_areaCountry.size().getInfo()} images areas from ImageCollection defined == ")
imC_areaCountry = imC_areaCountry.map(lambda im : get_number_ids(im))
imC_areaCountry = imC_areaCountry.sort('numId')
print("band name from the first image ==> ", imC_areaCountry.first().bandNames().getInfo())

# Rodando o metodo de Mann Kendall para todos 
# mann_Kendall_trend_test(imgCol_area)
print("inicializando o calculo de serie Harmonic")
for codeP in lst_Code[:]:    
    print(f"---- PROCESSING IMAGES AREAS OF {dictCodPais[codeP]}-----")
    # print("size geomet ", geomet.size().getInfo())
    # sys.exit()    
    if codeP == '4':        
        for idRegion in lstCodeReg:
            if int(idRegion) > 0:
                geomet = ee.FeatureCollection(param['regionsBr']).filter(
                            ee.Filter.eq('region', int(idRegion))).geometry()

                imgColReg_area = imC_areaCountry.filter(
                                            ee.Filter.eq('code_country', codeP)).filter(
                                                    ee.Filter.eq('code_region', idRegion))
                print("    with {} imnages area ".format(imgColReg_area.size().getInfo()))
                building_Harmonic_time_serie(imgColReg_area, codeP, idRegion, geomet)
                # contAuth = gerenciador(contAuth, param)
                

    else:
        geomet = ee.FeatureCollection(param['asset_panAm']).filter(
                        ee.Filter.eq('code', int(codeP)))
                        
        print("size geomet ", geomet.size().getInfo())
        geomet = geomet.geometry()

        imgCol_area = imC_areaCountry.filter(ee.Filter.eq('code_country', codeP))
        print("    with {} imnages area ".format(imgCol_area.size().getInfo()));      
        building_Harmonic_time_serie(imgCol_area, codeP, '', geomet)
        # contAuth = gerenciador(contAuth, param)

    

