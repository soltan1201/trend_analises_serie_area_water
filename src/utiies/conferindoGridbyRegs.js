/*
# Produzido por Geodatin - Dados e Geoinformacao
# DISTRIBUIDO COM GPLv2
# Observações in https://code.earthengine.google.com/faff12027c2892a3fa261fc4183a0695
*/



var params = {
    'assetBiomas': 'projects/mapbiomas-workspace/AUXILIAR/biomas_IBGE_250mil',
    'asset_grids': 'users/solkancengine17/shps_public/grid_5_5KM_AmericaL',
    'regions': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    'asset_input_br': 'projects/mapbiomas-workspace/TRANSVERSAIS/AGUA5-FT',
    'asset_gridBase': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/GRIDSTATS/GRIDBASE',
    'version': 11,

}
var dictCodPais = {
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
var dictCodPaisSig = {
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
var dictRegions = {
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

var dictRegSigla = {
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
var lst_Code = ['4'];  // '3','4','1','2','5','6','7','8','9' // 
var lstreg = [
        '11','12','13','14','15','16','17','18','19',
        '21','22','23','24','31','32','35','34','33',
        '41','42','44','45','46','47','51','52','53',
        '60'
    ]


var regionsBr = ee.FeatureCollection(params['regions'])
lstreg.forEach(function(reg){
    var regtmp = regionsBr.filter(ee.Filter.eq('region', parseInt(reg)))
    var nameGrids = 'grids_' + dictCodPaisSig[lst_Code[0]] +  "_" + dictRegSigla[reg] + "_" +  reg;
    var featGrids = ee.FeatureCollection(params.asset_gridBase + '/' + nameGrids)

    
    Map.addLayer(regtmp, {color: 'green'}, 'region ' + dictRegSigla[reg] + "_" +  reg, false);
    Map.addLayer(featGrids, {color: 'red'}, 'grid ' + dictRegSigla[reg] + "_" +  reg, false);
})

    