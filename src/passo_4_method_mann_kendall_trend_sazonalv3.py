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
    # 'asset_input': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/grade_area_to_imColBR',
    'asset_input': 'projects/nexgenmap/GTAGUA/grade_area_to_imColrbr',
    'asset_input_harm': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/MOSAIC/harmonic_imCol_area_AL',
    'asset_centroi': 'projects/mapbiomas-arida/Mapbiomas/grids_attr_centroid',
    'asset_geom': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/geometry_grade',
    # 'asset_output': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/stats_Kendall_BR23', 
    'asset_output': 'projects/nexgenmap/GTAGUA/stats_Kendall_BR23',
    # 'asset_output' : 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/MOSAIC/stats_Kendall_BR23',
    # 'asset_output1': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/stats_Kendall_AL',
    # 'asset_output': 'projects/nexgenmap/mosaic/stats_Kendall_AL',
    'regions': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
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
        # '100': 'solkanGeodatin',
        '100': 'solkan1201',   #      
        # '120': 'diegoUEFS',  
        '120': 'superconta'    
    },
    
}
class calculo_group(object):

    # contador = 1
    def __init__(self, imgCol):

        self.col_to_matches = imgCol
       
    def function_matches(self, img):
        
        def iterador_segundo(jj):
                return img.abs().eq(jj.abs())

        matches = self.col_to_matches.map(lambda kk: iterador_segundo(kk))
        matches = matches.sum()

        return img.multiply(matches.gt(1))
    
# # Rodando o metodo de Mann Kendall para todos 
class kendall_trend_sazonal(object):
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
     
    options = None
    def __init__(self, pmtros, codeCountry, idRegions):
        self.options = pmtros
        self.codCountry = codeCountry
        self.idRegion = idRegions
        
        self.imColArea = ee.ImageCollection(pmtros['asset_input']).filter(
                        ee.Filter.eq("code_country", codeCountry))
        print(f"====== Was loaded {self.imColArea.size().getInfo()} image Area =====")
        
        # get the geometry regions or country
        if str(codeCountry) == '4':
            print("load the regions of Brazil")
            self.imColArea = self.imColArea.filter(ee.Filter.eq('code_region',idRegions))
            self.geomet = ee.FeatureCollection(pmtros['regions']).filter(
                                    ee.Filter.eq('region', int(idRegions)))#.geometry()
            
        else:
            self.geomet = ee.FeatureCollection(pmtros['asset_panAm']).filter(
                                    ee.Filter.eq('code', int(codeCountry)))#.geometry()
            
        print(" geometry of área ", self.geomet.size().getInfo())
        self.geomet = self.geomet.geometry()
        
        print("inicializando o calculo de kendall")        
        
    def getDict_numId(self, lst_windowsYears):
        dictMonthY = {}
        for mmes in range(1, 13):
            lst_idNumY = []
            for iyear in lst_windowsYears:
                difYear = iyear - self.options['year_start']                
                numbId_tmp = int(difYear * 12) + int(mmes)
                lst_idNumY.append(numbId_tmp)
            dictMonthY[str(mmes)] = lst_idNumY
                
            # print(mmes, "  ", lst_idNumY)
            
        return dictMonthY
        
    def filterSystem_CalculateKendallIndex(self, lst_systemIndex):  # , dictNumIdsyst
        
        # area_guy_2022_area_9
        # building the list of year with month especific
        # lst_index = ["area_" + dictCodPaisSig[codeP] + "_" + str(yyear) + "_area_" + str(mmonth) for yyear in wls_year]
        # print(" ", lst_index)
        
        mydictNumIdYear = self.getDict_numId(lst_systemIndex)
        # adicionando os indices de Kendall Mann desde o valor 0
        indice_Kendall = ee.Image.constant(0).int16()
        p_value_kendall_mean = ee.Image.constant(0).int16()
        
        
        for kk, vlist_mes in mydictNumIdYear.items():
            print(f" *** PORCESSIN MONTH {kk} ***")
            # a image Collection já está no pais ou region bioma especifico
            img_Col_sazonal = self.imColArea.filter(ee.Filter.inList('numId', vlist_mes))
            # img_Col_sazonal = img_Col_sazonal.map(lambda img: img.set('numId', mydictNumId.get('system:index')))
            # print()
            afterFilter = ee.Filter.lessThan(
                                        leftField= 'numId', #'system:start',
                                        rightField= 'numId' #'system:start'
                                    )
            joined_imgCol = ee.ImageCollection(ee.Join.saveAll('after')
                                .apply(
                                    primary= img_Col_sazonal,
                                    secondary= img_Col_sazonal,
                                    condition= afterFilter
                                ))
            # print("images collections joined ", joined_imgCol.size().getInfo())
            # sys.exit()
            kendall_ind = joined_imgCol.map(lambda col_current: self.indicador_mann_kendall(col_current))
            kendall_ind = ee.ImageCollection(kendall_ind.flatten()).reduce('sum', 2)

            indice_Kendall = indice_Kendall.add(kendall_ind)
        
            if self.options['calc_pValue']:

                # # Values that are in a group (ties).  Set all else to zero.
                # ##################################################
                # ##### Compute tie group sizes in a sequence. ##### 
                # ##### The first group is discarded.          #####
                # ##################################################
                def agrupar_ties (marray):

                    length = marray.arrayLength(0)
                    # array of indices. There are 1-indice

                    indices = ee.Image([1]).arrayRepeat(0, length).arrayAccum(
                                                0, ee.Reducer.sum()).toArray(1)
                    
                    sorted = marray.arraySort()
                    left = sorted.arraySlice(0, 1)
                    right = sorted.arraySlice(0, 0, -1)

                    # indices of the end of runs
                    # Always keep the last index, the end of the sequence.
                    mask = left.neq(right).arrayCat(  
                                        ee.Image(ee.Array([[1]])), 0)

                    runIndices = indices.arrayMask(mask)

                    # Subtract the indices to get run lengths.
                    groupSizes = runIndices.arraySlice(0, 1).subtract(
                                                runIndices.arraySlice(0, 0, -1))
                    
                    return groupSizes
            
                nn = len(vlist_mes)
                total = nn * (nn - 1) * (2 * nn + 5)

                # See equation 2.6 in Sen (1968).
                def factors(img):
                    return ee.Image(img).expression('b() * (b() - 1) * (b() * 2 + 5)')

                funct_group_size = calculo_group(img_Col_sazonal)
                groups = img_Col_sazonal.map(lambda ff : funct_group_size.function_matches(ff))
                groupSizes = agrupar_ties(groups.toArray())

                # print()
                groupFactors = factors(groupSizes)
                groupFactorSum = groupFactors.arrayReduce('sum', [0]).arrayGet([0, 0])

                count = joined_imgCol.count()

                kendallVariance = factors(count).subtract(groupFactorSum).divide(18).float()


                # Compute Z-statistics.
                zero = indice_Kendall.multiply(indice_Kendall.eq(0))
                pos = indice_Kendall.multiply(indice_Kendall.gt(0)).subtract(1)
                neg = indice_Kendall.multiply(indice_Kendall.lt(0)).add(1)

                zeta = zero.add(pos.divide(kendallVariance.sqrt())).add(
                                neg.divide(kendallVariance.sqrt()))
                
                #// https://en.wikipedia.org/wiki/Error_function#Cumulative_distribution_function

                def eeCdf(zz):
                    return ee.Image(0.5).multiply(
                                    ee.Image(1).add(ee.Image(zz).divide(ee.Image(2).sqrt()).erf()))

                def invCdf(pp):
                    return ee.Image(2).sqrt().multiply(
                                    ee.Image(pp).multiply(2).subtract(1).erfInv())

                # Compute P-values
                pp = ee.Image(1).subtract(eeCdf(zeta.abs()))
                p_value_kendall_mean = p_value_kendall_mean.add(pp)
        
        name_im = "mann_kendall_trend_test_p_value_cor2022"
        p_value_kendall_mean = p_value_kendall_mean.reduce(ee.Reducer.min()).clip(self.geomet).rename('p_value')
        # já não se applica 
        # exportarImagem(p_value_kendall_mean.reduce(ee.Reducer.minMax()).clip(geomet), name_im, geomet)
        for p_value in [0.05]: #0.025, 0.005, 0.05 , 0.005, 
            name_im = "mann_kendall_watter_sazonal_p_"+ str(p_value)[2:] + "_" 
            addIndicador = ''
            if str(self.codCountry) == '4':
                addIndicador = self.dictCodPaisSig[self.codCountry] +  "_" + self.dictRegSigla[self.idRegion] + "_" + self.idRegion + "_" 
            else:
                addIndicador = self.dictCodPaisSig[self.codCountry] +  "_"
            name_im = name_im + addIndicador + str(lst_systemIndex[0]) + "_" + str(lst_systemIndex[-1]) 
            
            ind_kendall_exp = indice_Kendall.clip(self.geomet)
            ind_kendall_exp = ind_kendall_exp.updateMask(p_value_kendall_mean.lt(p_value)).rename('kendall')   #
            ind_kendall_exp = ee.Image(ind_kendall_exp).set(
                                            'p-value', str(p_value)[2:],
                                            'version', 11, 
                                            'region', self.idRegion,
                                            'country', self.codCountry,
                                            'interval', str(lst_systemIndex[0]) + "_" + str(lst_systemIndex[-1])
                                            )
            
            self.exportarImagem(ind_kendall_exp, name_im, self.geomet)
            
    def indicador_mann_kendall (self, current):

        def signal_function (i_im, j_im):
            return ee.Image(j_im).neq(i_im).multiply( 
                            ee.Image(j_im).subtract(i_im).clamp(-1, 1))

        afterCollection = ee.ImageCollection.fromImages(current.get('after'))
        # The unmask is to prevent accumulation of masked pixels that
        # result from the undefined case of when either current or image
        # is masked.  It won't affect the sum, since it's unmasked to zero.
        def compare_sign (img):
            return ee.Image(signal_function(current, img)).unmask(0)
        
        afterCollection = afterCollection.map(lambda imgg : compare_sign(imgg))

        return afterCollection

    def exportarImagem(self, imgU, nameAl, geomet):    
        
        IdAsset = self.options['asset_output'] + "/" + nameAl   
        
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


##################################################################################
#####   MAIN                                                              ########
##################################################################################

def get_number_ids(img):

    numid = img.get('system:index')
    numid = ee.String(numid).replace('area_', '')
    numid = ee.Number.parse(numid).int16()
    val_yy = numid.divide(12).floor().add(1985)     
    cc = numid.add(1).mod(12)
    cc = ee.Algorithms.If(ee.Algorithms.IsEqual(
                                ee.Number(cc).eq(0), 1), ee.Number(12), cc )
    
    dat_year = ee.Date.fromYMD(val_yy, cc, 1)
    return img.rename(['area']).set('numId', numid, 'system:start', dat_year)

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
        return 0    
    cont += 1    
    return cont

SaveList = False
specificLastYear = False 
allCountry = False
countryName = 'bra'
lst_year = [kk for kk in range(param['year_start'], param['year_end'] + 1)]
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
            lstTempYears = lst_year[ii: window + ii]
            print("{} : windows {} : {} ".format(contador, window, lstTempYears))
            if specificLastYear:
                if param['year_end'] in lstTempYears:
                    lista_Windows_years.append(lstTempYears)
            else:
                lista_Windows_years.append(lstTempYears)
            contador += 1
    
    window -= 1
if allCountry:
    imgColTendc =  ee.ImageCollection(param['asset_output'])#.merge(
                                # ee.ImageCollection(param['asset_output1'])
                            # )#.filter(ee.Filter.eq('name_country', 'Brasil'))
    print("images tendencias Kendal ", imgColTendc.size().getInfo())
else:
    if countryName == 'bra':
        imgColTendc = ee.ImageCollection(param['asset_output']#)#.merge(
                                # ee.ImageCollection(param['asset_output1'])
                            ).filter(ee.Filter.eq('name_country', 'Brasil'))
        print("images para analisar tendencias de Kendal ", imgColTendc.size().getInfo())

lstSystemIndexImg = imgColTendc.reduceColumns(ee.Reducer.toList(), ['system:index']).get('list').getInfo()
print("    ", lstSystemIndexImg[:2])

if SaveList: 
    arqReg = open("anliseSystemIndexTendencia.txt", 'w+')
    for iimg in  lstSystemIndexImg[:]:
        # print("    ", iimg)
        arqReg.write(iimg + '\n')
    arqReg.close()
# sys.exit()

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
print(f"--- the list of years windows have {len(lista_Windows_years)} lists --- ")
# sys.exit()
# lst_Code = ['8','9'];  # '1','3','5', # '2','4'==>  '2','6','7','8','9',
lst_Code = ['4'];
lstreg = [
        # '11','33',
        '12','13','14','15','16','17','18','19',
        '21','22','23','24','31','32','34','35',          
        '41','42','44','45','46','47','51','52',
        '53', '60'
]
cont = 0
indP = 'p_05'
cont = gerenciador(cont, param)
for codeP in lst_Code[:2]:    
    print("========== processing code ==> ", codeP)
    if codeP == '4':
        for regionCod in lstreg:           
            ccKendall_trend_sazonal = kendall_trend_sazonal(param, codeP, regionCod)
            for cc, wls_year in enumerate(lista_Windows_years[:]):            
                # dictSystemInd = getDict_numId(lst_index, mmonth)
                year_start = wls_year[0]
                year_end = wls_year[-1]
                lst_indexSys = []
                sufixo = 'mann_kendall_watter_sazonal_'
                sufixo1 = '1_mann_kendall_watter_sazonal_'
                sufixo2 = '2_mann_kendall_watter_sazonal'
                prefixo = str( wls_year[0]) + '_' + str(wls_year[-1])
                
                indiceSystem = sufixo + indP + '_' + dictCodPaisSig[codeP] + '_' + dictRegSigla[regionCod] + '_' + regionCod + '_' + prefixo
                indiceSystem1 = sufixo1 + indP + '_' + dictCodPaisSig[codeP] + '_' + dictRegSigla[regionCod] + '_' + regionCod + '_' + prefixo
                indiceSystem2 = sufixo2 + indP + '_' + dictCodPaisSig[codeP] + '_' + dictRegSigla[regionCod] + '_' + regionCod + '_' + prefixo
                print("   ", indiceSystem)
                print("   ", indiceSystem2)
                # img_tmp = imgColTendc.filter(ee.Filter.eq('system:index', indiceSystem))
                # sizeImExist = img_tmp.size().getInfo()
                if (indiceSystem not in lstSystemIndexImg) and (
                        indiceSystem1 not in lstSystemIndexImg) and (
                            indiceSystem2 not in lstSystemIndexImg):
                # if 2023 not in wls_year:
                    ccKendall_trend_sazonal.filterSystem_CalculateKendallIndex(wls_year)
                    cont = gerenciador(cont, param)
    else:
        ccKendall_trend_sazonal = kendall_trend_sazonal(param, codeP, None)    
        for wls_year in lista_Windows_years[:]:            
            # dictSystemInd = getDict_numId(lst_index, mmonth)
            # year_start = wls_year[0]
            # year_end = wls_year[-1]
            # lst_indexSys = []
            # sufixo = 'mann_kendall_watter_sazonal_'
            # prefixo = str( wls_year[0]) + '_' + str(wls_year[-1])
            # indiceSystem = sufixo + indP + "_" + dictCodPaisSig[codeP] + "_" + prefixo
            # print("verificando por => ", indiceSystem)
            # img_tmp = imgColTendc.filter(ee.Filter.eq('system:index', indiceSystem))
            # sizeImExist = img_tmp.size().getInfo()
            # if sizeImExist < 1:
            print("--- processing ---")
            ccKendall_trend_sazonal.filterSystem_CalculateKendallIndex(wls_year)
            cont = gerenciador(cont, param)
            
    