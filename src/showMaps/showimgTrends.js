
function setpvalue(img){
    var idImg = img.id();
    var pvalue05 = idImg.index('_p_005_')
    return img
}

// var asset_trend = 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/MOSAIC/stats_Kendall_BR23';
// var asset_trend = 'projects/nexgenmap/GTAGUA/stats_Kendall_BR23';
var asset_trend = 'projects/nexgenmap/GTAGUA/stats_Kendall_br23'
var imgColtrend =ee.ImageCollection(asset_trend);
print("we have loaded imageCollection with size = ", imgColtrend.size());
print("show metadata trends layers ", imgColtrend.limit(500));
var lstinterv = imgColtrend.reduceColumns(ee.Reducer.toList(), ['interval']).get('list');

lstinterv = ee.List(lstinterv).distinct();
print('lista de intervalos ', lstinterv);

var trendSpe = imgColtrend.filter(ee.Filter.eq('interval', '1985_2024')).mosaic();
print(trendSpe)
Map.addLayer(trendSpe, {min: -1, max: 1, palette: ['FF0000','FFFFFF', '00FF00']}, 'trend')