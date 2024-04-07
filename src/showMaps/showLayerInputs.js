
function getPolygonsfromFolder(dictPath){
    var getlistPlgs = ee.data.getList(dictPath);
    var lstFiles = [];
    var namepath;
    getlistPlgs.forEach(function(npath){
        namepath = npath.id.split("/")[-1];
        lstFiles.push(namepath);
    });
    print(ee.String(" we have ").cat(lstFiles.length.toString()).cat(' files grades'));
    return lstFiles;
}


var param = {
    'asset_asset_gradesArea': {'id': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/GRIDSTATS/versionPanAm_4'},
    'asset_ImgArea': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/grade_area_to_imColAL',
    'asset_inputBR': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/grade_area_to_imCol',
    'asset_centroi': 'projects/mapbiomas-arida/Mapbiomas/grids_attr_centroid',
    'asset_imgHamonicArea': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/MOSAIC/harmonic_imCol_area_AL',
    'asset_panAm': 'projects/mapbiomas-agua/assets/territories/countryPanAmazon',
    'regionsBr': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
};
// ========== territo ou limites utilizados =================
var territoriosPais = ee.FeatureCollection(param.asset_panAm);
var regioesBr = ee.FeatureCollection(param.regionsBr); 
print("show the regions properties ", regioesBr);

var imgColBra = ee.ImageCollection(param.asset_ImgArea).filter(ee.Filter.eq('code_country', '4'));
print("image Collection filtered to Brasil country ", imgColBra.limit(4));
print(imgColBra.filter(ee.Filter.eq('code_region', '11')));

// =================== dados Harmonicos =====================
var imgColHarmo = ee.ImageCollection(param.asset_imgHamonicArea);
print("show the first 4 files images", imgColHarmo.limit(4));
print("size of ImageCollection ", imgColHarmo.size());

// ============== files grades ==============================
var lstGradesFile = getPolygonsfromFolder(param.asset_asset_gradesArea);


Map.addLayer(territoriosPais, {color: 'green'}, 'territorios');
Map.addLayer(regioesBr, {color: 'Orange'}, 'regions');


