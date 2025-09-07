
var vis = {
    areawater: {
        min: 0, max: 25,
        palette : ['#000000',"#D6E4FF",'#A7E6FF','#3ABEF9','#3572EF','#1c1cf0 ','#050C9C']
    },
    layerwater: {
        min: 0, max: 1,
        palette : ['#000000','#1c1cf0']
    },


}

var param = {
    // 'asset_asset_gradesArea': {'id': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/GRIDSTATS/versionPanAm_4'},
    'asset_asset_gradesArea': {'id': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/GRIDSTATS/version11_br'},
    'asset_asset_gradesArea2': {'id': 'projects/nexgenmap/GTAGUA/GRIDSTATS/version11_br'},
    // 'asset_water': 'projects/nexgenmap/TRANSVERSAIS/AGUA5-FT',
    'asset_water': 'projects/mapbiomas-ecuador/assets/MAPBIOMAS-WATER/COLECCION3/ECUADOR/FINAL-ASSETS/water-surface-03',
    'asset_centroi': 'projects/mapbiomas-arida/Mapbiomas/grids_attr_centroid',
    // 'asset_input': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/grade_area_to_imColBR',
    'asset_input': 'projects/nexgenmap/GTAGUA/grade_area_to_imColrbr',
    'asset_panAm': 'projects/mapbiomas-agua/assets/territories/countryPanAmazon',
    'asset_grids': 'users/solkancengine17/shps_public/grid_5_5KM_AmericaL',
    'regions': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    'asset_gridBase': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/GRIDSTATS/GRIDBASE',
}
var codeCountry = '5';
var layerWater = ee.ImageCollection(param.asset_water)
                            .filter(ee.Filter.eq('version', '2'))
print("show layer water ", layerWater.limit(3));
print(" how many images ", layerWater.size());
var shpCountries = ee.FeatureCollection(param.asset_panAm)
                      .filter(ee.Filter.eq("code", parseInt(codeCountry)));
// Map.addLayer(shpCountries , {color: '#3D0B0AFF'}, 'regions');
print("show metadata countries ", shpCountries);
var imColArea = ee.ImageCollection(param.asset_input)
                      .filter(ee.Filter.eq("code_country", codeCountry));

print("layer area water ", imColArea.limit(10));
var lstMeses = [ 2, 200, 350, 450, 468, 478];
var areamonth2;
lstMeses.forEach(function(mes){
    areamonth2 = imColArea.filter(ee.Filter.eq('numId', mes))
                          .filter(ee.Filter.neq('numberId', mes))
                          .mosaic()
    var nyear = 1985 + parseInt(mes/ 12);
    var month = mes % 12;
    print("year ", nyear);
    print('month ', month);
    if (month === 0){
        month = 12;
    }
    var watertmp = layerWater
                      .filter(ee.Filter.eq('cadence', 'monthly'))
                      .filter(ee.Filter.eq('year', nyear));    
                      
    
    var imagename = String(nyear) + "_mes_" + String(month + 1);
    var bandaAct = 'w_' + String(month);
    print("ver imagens " + bandaAct, watertmp);
    Map.addLayer(watertmp.select(bandaAct), vis.layerwater, imagename, false);
    Map.addLayer(areamonth2, vis.areawater, 'mes ' + String(mes), false);
})

var outline = ee.Image().byte().paint({
    featureCollection: shpCountries,
    color: 1,
    width: 2
  });
Map.addLayer(outline, {palette: 'FF0000'}, 'edges');