function setpvalue(img){
    var idImg = img.id();
    var pvalue05 = idImg.index('_p_005_')
    return img
}
var country_id = '5';

var vis = {
    layer_trend: {min: -1, max: 1, palette: ['FF0000','FFFFFF', '00FF00']},
    layerwater: {
        min: 0, max: 1,
        palette : ['#000000','#1c1cf0']
    },


}

var asset_superficie_water = 'projects/mapbiomas-ecuador/assets/MAPBIOMAS-WATER/COLECCION3/ECUADOR/FINAL-ASSETS/water-surface-03';
var layerWater = ee.ImageCollection(asset_superficie_water)
                            .filter(ee.Filter.eq('version', '2'))
print("show layer water ", layerWater.limit(3));


// var asset_trend = 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/MOSAIC/stats_Kendall_BR23';
// var asset_trend = 'projects/nexgenmap/GTAGUA/stats_Kendall_BR23';
var asset_trend = 'projects/nexgenmap/GTAGUA/stats_Kendall_br23'
var imgColtrend = ee.ImageCollection(asset_trend)
                      .filter(ee.Filter.eq('country', country_id));
print("we have loaded imageCollection with size = ", imgColtrend.size());
print("show metadata trends layers ", imgColtrend.limit(5));
var lstinterv = imgColtrend.reduceColumns(ee.Reducer.toList(), ['interval']).get('list');

lstinterv = ee.List(lstinterv).distinct();
print('lista de intervalos ', lstinterv);

var trendSpe = imgColtrend.filter(ee.Filter.eq('interval', '1985_2024')).mosaic();
print("show metadata of trend  ", trendSpe);

var bandaAct = 'w_1';
var watertmp85 = layerWater.filter(ee.Filter.eq('cadence', 'monthly'))
                      .filter(ee.Filter.eq('year', 1985));  

var watertmp24 = layerWater.filter(ee.Filter.eq('cadence', 'monthly'))
                      .filter(ee.Filter.eq('year', 2024));  

Map.addLayer(watertmp85.select(bandaAct), vis.layerwater, 'superficie 85', false);
Map.addLayer(watertmp24.select(bandaAct), vis.layerwater, 'superficie 24', false);
Map.addLayer(trendSpe, vis.layer_trend, 'trend')