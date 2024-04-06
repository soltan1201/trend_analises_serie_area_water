
var asset_harmonic = 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/MOSAIC/harmonic_imCol_area_AL';
var imgColHarmo = ee.ImageCollection(asset_harmonic);

print(imgColHarmo.limit(4));


var param = {
    'asset_ImgArea': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/grade_area_to_imColAL',
    'asset_inputBR': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/grade_area_to_imCol',
    'asset_centroi': 'projects/mapbiomas-arida/Mapbiomas/grids_attr_centroid',
    'asset_output': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/MOSAIC/harmonic_imCol_area_AL',
    'asset_panAm': 'projects/mapbiomas-agua/assets/territories/countryPanAmazon',
    'regionsBr': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
};

var territoriosPais = ee.FeatureCollection(param.asset_panAm);
var regioesBr = ee.FeatureCollection(param.regionsBr); 
print("show the regions properties ", regioesBr);


var imgColBra = ee.ImageCollection(param.asset_ImgArea).filter(ee.Filter.eq('code_country', '4'));
print("image Collection filtered to Brasil country ", imgColBra.limit(4));
print(imgColBra.filter(ee.Filter.eq('code_region', '11')));


Map.addLayer(territoriosPais, {color: 'green'}, 'territorios');
Map.addLayer(regioesBr, {color: 'Orange'}, 'regions');


