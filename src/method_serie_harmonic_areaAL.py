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
import numpy as np
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
    'asset_inputBR': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/grade_area_to_imCol',
    'asset_centroi': 'projects/mapbiomas-arida/Mapbiomas/grids_attr_centroid',
    'asset_output': 'projects/nexgenmap/mosaic/harmonic_imCol_area_AL',
    'asset_panAm': 'projects/mapbiomas-agua/assets/territories/countryPanAmazon',
    'numeroTask': 1,
    'numeroLimit': 200,
    'conta' : {
        '0': 'caatinga01',        
        '30': 'caatinga02',
        '60': 'caatinga03',
        '90': 'caatinga04',
        '120': 'caatinga05',
        '140': 'solkan1201',   #      
        '160': 'diegoGmail',  
        '180': 'superconta'   
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
        gee.switch_user(paramet['conta'][str(cont)])
        gee.init()        
        gee.tasks(n= paramet['numeroTask'], return_list= True)        
    
    elif cont > paramet['numeroLimit']:
        cont = 0
        return cont
    
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

lst_Code = ['8','9'];  # '1','2','3','5','6','7',
# code_country
imC_areaCountry = ee.ImageCollection(param['asset_input']).filter(ee.Filter.inList('code_country', lst_Code))
imgCol_areaBr = ee.ImageCollection(param['asset_input'])

imC_areaCountry = imC_areaCountry.map(lambda im : get_number_ids(im))
imC_areaCountry = imC_areaCountry.sort('numId')
print(imgCol_areaBr.first().bandNames().getInfo())
sys.exit()


geomet_panAm = ee.FeatureCollection(param['asset_panAm'])

var_dependent = 'area'
var_independent = ['constant', 't', 'cos', 'sin']
all_variables = ['constant', 't', 'cos', 'sin', 'area']

print("inicializando o calculo de serie Harmonic")
for codeP in lst_Code[:]:    
    print(f"---- PROCESSING IMAGES AREAS OF {dictCodPais[codeP]}-----")
    imgCol_area = imC_areaCountry.filter(ee.Filter.eq('code_country', codeP))
    print("    with {} imnages area ".format(imgCol_area.size().getInfo()));
    
    geomet = geomet_panAm.filter(ee.Filter.eq('code', int(codeP))).geometry()
    # print("size geomet ", geomet.size().getInfo())
    # sys.exit()
    img_col_addTemp = imgCol_area.map(lambda img: addVariables_tempo(img));
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
    calculo_harmonico = calculo_harmonic(array_Trend_Coef, geomet, param['asset_output'])
    # fittedHarmonicM = img_col_addTemp.map(lambda img : calculo_harmonico.estimate_harmonic_area(img))

    fittedHarmonicM = img_col_addTemp.map(lambda img : img.addBands(img.select(var_independent).multiply(  
                                array_Trend_Coef).reduce('sum').rename('area_harmonic')))

    fittedHarmonicM = fittedHarmonicM.select(['area', 'area_harmonic'])
    print(fittedHarmonicM.first().bandNames().getInfo())
    # print(fittedHarmonicM.first().get('system:index').getInfo())
    contAuth = 0
    

    for ii in range(1, 457):
        print("processando a imagem # {} ".format(ii))
        
        img_band = 'area_' + str(ii)
        img_tmp =  fittedHarmonicM.filter(ee.Filter.eq('numId', ii)).first()
        
        img_tmp = img_tmp.set('system:index', img_band)
        # img_tmp = img_tmp.clip(geomet).set('system:footprint', geomet)
        img_tmp = img_tmp.set('numId', ii)
        img_tmp = img_tmp.set('code_country', codeP)

        name_im = 'area_harmonic_' + dictCodPaisSig[codeP] + "_" + str(ii)
        exportarImagem(img_tmp, name_im, geomet)
        contAuth = gerenciador(contAuth, param)

# Rodando o metodo de Mann Kendall para todos 
# mann_Kendall_trend_test(imgCol_area)