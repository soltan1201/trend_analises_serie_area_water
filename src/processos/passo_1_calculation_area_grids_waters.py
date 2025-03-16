#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
# SCRIPT DE CALCULO DE AREA DE AGUA POR GRIDS
# Produzido por Geodatin - Dados e Geoinformacao
# DISTRIBUIDO COM GPLv2
# Observações in https://code.earthengine.google.com/faff12027c2892a3fa261fc4183a0695
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
# sys.setrecursionlimit(1000000000)


params = {
    'assetBiomas': 'projects/mapbiomas-workspace/AUXILIAR/biomas_IBGE_250mil',
    'asset_panAm': 'projects/mapbiomas-agua/assets/territories/countryPanAmazon',
    'asset_grids': 'users/solkancengine17/shps_public/grid_5_5KM_AmericaL',
    'regions': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    'asset_input_panAm': 'projects/mapbiomas-raisg/PRODUCTOS/AGUA/COLECCION01/water-integracion-02',
    'asset_input_br': 'projects/nexgenmap/TRANSVERSAIS/AGUA5-FT',    
    # 'asset_output': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/GRIDSTATS/versionPanAm_4',
    # 'asset_output': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/GRIDSTATS/version11_br',
    'asset_output': 'projects/nexgenmap/GTAGUA/GRIDSTATS/version11_br',
    'asset_gridBase': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/GRIDSTATS/GRIDBASE',
    'version': 11,
    'numeroTask': 3,
    'numeroLimit': 60,
    'conta' : {
        '0': 'caatinga01',
        '5': 'caatinga02',
        '10': 'caatinga03',
        '15': 'caatinga04',
        '20': 'caatinga05',
        # '25': 'solkanGeodatin',
        '25': 'solkan1201',   #      
        '30': 'superconta'       
    },
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
version = params['version']
class calculation_water_area(object):
    version = None
    options = None
    lstYears = [
        '1985', '1986', '1987', '1988', '1989', '1990', '1991', '1992', '1993', '1994', '1995', 
        '1996', '1997', '1998', '1999', '2000', '2001', '2002', '2003', '2004', '2005', '2006', 
        '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', 
        '2018', '2019', '2020', '2021', '2022','2023','2024'
    ]
    def __init__(self, nparams, nvers, myCodeCountry):
        self.version = nvers
        self.options = nparams
        if myCodeCountry == '4':
            print("**************** loadinf asset BR *******************")
            self.imgColWater = ee.ImageCollection(nparams['asset_input_br']).filter(
                        ee.Filter.eq("version", str(nvers)))
        else:
            self.imgColWater = ee.ImageCollection(nparams['asset_input_panAm']).filter(
                        ee.Filter.eq("version", nvers))

        print(f"      Were loaded {self.imgColWater.size().getInfo()} images from ImgCol ")

        self.regions = ee.FeatureCollection(nparams['regions'])

        self.annual_img = None
        self.monthly_img = None

    def calc_area (self, mask, geom):

        ndict = ee.Image.pixelArea().divide(1000000
                            ).updateMask(mask
                                ).reduceRegion(
                                    reducer= ee.Reducer.sum(), 
                                    geometry= geom, 
                                    scale= 30, 
                                    bestEffort= True, 
                                    maxPixels= 1e13, 
                                );
  
        area = ee.Number(ndict.get("area"));  
        return area

    def calcularAreaMonth(self, featGrid, nyear):
        geoGrid = featGrid.geometry()

        area_annual = self.calc_area(self.annual_img, geoGrid);
        area_1 =  self.calc_area(self.monthly_img.select("classification_1") , geoGrid);
        area_2 =  self.calc_area(self.monthly_img.select("classification_2") , geoGrid);
        area_3 =  self.calc_area(self.monthly_img.select("classification_3") , geoGrid);
        area_4 =  self.calc_area(self.monthly_img.select("classification_4") , geoGrid);
        area_5 =  self.calc_area(self.monthly_img.select("classification_5") , geoGrid);
        area_6 =  self.calc_area(self.monthly_img.select("classification_6") , geoGrid);
        area_7 =  self.calc_area(self.monthly_img.select("classification_7") , geoGrid);
        area_8 =  self.calc_area(self.monthly_img.select("classification_8") , geoGrid);
        area_9 =  self.calc_area(self.monthly_img.select("classification_9") , geoGrid);
        area_10 = self.calc_area(self.monthly_img.select("classification_10"), geoGrid);
        area_11 = self.calc_area(self.monthly_img.select("classification_11"), geoGrid);
        area_12 = self.calc_area(self.monthly_img.select("classification_12"), geoGrid);

        return featGrid.set(
                "year", nyear).set(
                "area_annual", area_annual).set(
                "area_1", area_1).set(
                "area_2", area_2).set(
                "area_3", area_3).set(
                "area_4", area_4).set(
                "area_5", area_5).set(
                "area_6", area_6).set(
                "area_7", area_7).set(
                "area_8", area_8).set(
                "area_9", area_9).set(
                "area_10", area_10).set(
                "area_11", area_11).set(
                "area_12", area_12)


    def iter_by_years_calculeArea(self, shpsGrids, nameEx, nameBioma, codReg):    

        for yyear in self.lstYears[-2:]:            
            print("processing year ", yyear)
            nameWaterYear = nameBioma + '-' + yyear + '-' + str(self.version)
            nameWaterMonths = nameBioma + '-' + yyear + '-' + str(self.version) + '_mensal'
            if str(yyear) == '2024':
                nameWaterMonths = nameBioma + '-' + yyear + '-' + str(self.version) + '_mensal_validation'
            print("mensal Index >>>> ", nameWaterMonths)
            self.annual_img = self.imgColWater.filter( ee.Filter.eq("system:index", nameWaterYear));
            # .filter(ee.Filter.eq('cadence', 'annual')).filter(
            #                                     ee.Filter.eq('year', yyear)); 
            print("checking anual", self.annual_img.size().getInfo())
            self.monthly_img = self.imgColWater.filter(ee.Filter.eq("system:index", nameWaterMonths));
            # .filter(ee.Filter.eq('cadence', 'monthly')).filter(
            #                                     ee.Filter.eq('year', yyear));
            print("checking mensal", self.monthly_img.first().bandNames().getInfo())
            regionsLocal = self.regions.filter(ee.Filter.eq('region', int(codReg))).geometry()
            if yyear == 1985:
                print("annual_img " + nameWaterYear + " ==> ", self.annual_img.size().getInfo())
                print("monthly_img " + nameWaterMonths + " ==> ", self.monthly_img.size().getInfo())
                print("")
            else:
                print(f"loading {nameWaterYear} and {nameWaterMonths} ")

            # sys.exit()
            self.annual_img = self.annual_img.first().clip(regionsLocal);
            self.monthly_img = self.monthly_img.first().clip(regionsLocal);
            # sys.exit()
            #  fazer uma clasee 
            grids_attr = shpsGrids.map(lambda feat : self.calcularAreaMonth(feat, yyear))

            name_export = nameEx + '_' + yyear
            self.processoExportar(grids_attr, name_export) 
            

    #exporta a imagem classificada para o asset
    def processoExportar(self, areaFeat, nameT):      
        assetOutput = self.options['asset_output'] + "/" + nameT
        optExp = {
            'collection': areaFeat, 
            'description': nameT, 
            'assetId': assetOutput       
            }    
        task = ee.batch.Export.table.toAsset(**optExp)
        task.start() 
        print("Exportando ... " + nameT + "..!")  



def gerenciador(cont, paramet):    
    #0, 18, 36, 54]
    #=====================================#
    # gerenciador de contas para controlar# 
    # processos task no gee               #
    #=====================================#
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

lst_Code = ['4'];  # '3','4','1','2','5','6','7','8','9' // 
lstreg = [
        # '11', '12','13','14','15','16','17','18','19',
        '20',
        # '21','22','23','24','31', '32','35',
        # '34', '33','41', 
        # '42','43', '44', '45','46',
        # '47','51','52','53', '60'                
    ]

cont = 30
cont = gerenciador(cont, params)
# regionsBr = ee.FeatureCollection(params['regions'])
limitAmazonia = ee.FeatureCollection(params['asset_panAm']);                       
print("limite de Amazonia ", limitAmazonia.size().getInfo())
# sys.exit()

for codeP in lst_Code:
    cCalculantion_water_area = calculation_water_area(params, version, codeP)   
    # sys.exit()
    if codeP == '4':
        print("processing codigo 4 ==> Brasil")
        
        for regionCod in lstreg:
            nameGrids = 'grids_' + dictCodPaisSig[codeP] + '_' + dictRegSigla[regionCod] + '_' + regionCod
            featGrids = ee.FeatureCollection(params['asset_gridBase'] + '/' + nameGrids)
            sizeFeat = featGrids.size().getInfo()
            print(f"<--- PROCESSING {sizeFeat} GRIDS IN {nameGrids} ---->")
            nameGridsEx = 'grids_attr_area_' + dictCodPaisSig[codeP] + '_' + dictRegSigla[regionCod] + '_' + regionCod
            print("name export Area Gride ", nameGridsEx)
            cCalculantion_water_area.iter_by_years_calculeArea(featGrids, nameGridsEx, dictRegions[regionCod], regionCod)
            cont = gerenciador(cont, params)
            # sys.exit()

    else:
        nameGrids = 'grids_' + dictCodPaisSig[codeP] 
        featGrids = ee.FeatureCollection(params['asset_gridBase'] + '/' + nameGrids)
        sizeFeat = featGrids.size().getInfo()
        print(f"<--- PROCESSING {sizeFeat} GRIDS IN {nameGrids} ---->")
        nameGridsEx = 'grids_attr_area_' + dictCodPaisSig[codeP]
        cCalculantion_water_area.iter_by_years_calculeArea(featGrids, nameGridsEx)
        # cont = gerenciador(cont, params)