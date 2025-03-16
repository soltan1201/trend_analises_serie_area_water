
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

function GetPolygonsfromFolder(dictAsset){
    var getlistPtos = ee.data.getList(dictAsset)
    var ColectionPtos = []
    
    getlistPtos.forEach(function(idAsset){
        var path_ = idAsset['id']
        // print("Reading ", path_)
        ColectionPtos.push(path_)
    })
    return ColectionPtos
}

var param = {
    // 'asset_asset_gradesArea': {'id': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/GRIDSTATS/versionPanAm_4'}, #
    // 'asset_asset_gradesArea': {'id': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/GRIDSTATS/version11_br'},
    'asset_asset_gradesArea': {'id': 'projects/nexgenmap/GTAGUA/GRIDSTATS/version11_br'},
    'asset_water': 'projects/mapbiomas-workspace/TRANSVERSAIS/AGUA5-FT',
    'asset_centroi': 'projects/mapbiomas-arida/Mapbiomas/grids_attr_centroid',
    'asset_input': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/grade_area_to_imColAL',
    'asset_panAm': 'projects/mapbiomas-agua/assets/territories/countryPanAmazon',
    'asset_grids': 'users/solkancengine17/shps_public/grid_5_5KM_AmericaL',
    'regions': 'users/geomapeamentoipam/AUXILIAR/regioes_biomas_col2',
    'asset_gridBase': 'projects/mapbiomas-workspace/AMOSTRAS/GTAGUA/GRIDSTATS/GRIDBASE',
}

var layerWater = ee.ImageCollection(param.asset_water).filter(ee.Filter.eq('version', '11'))
print("show layer water ", layerWater.limit(3));
print(" how many images ", layerWater.size());
var regions = ee.FeatureCollection(param.regions);
var codeCountry = '4';
var nregion = '24';
var lstyears = ['2023','2024'];
var featColsArea = GetPolygonsfromFolder(param.asset_asset_gradesArea)
featColsArea.forEach(function(pathArea){
    // print("loading ", pathArea)
    var partes = pathArea.split('/');
    var namefile = partes[partes.length - 1];
    // print(" loading name file " + namefile);
    partes = namefile.split("_")
    var yyear = partes[partes.length - 1];
    var yregion = partes[partes.length - 2];
    // 
    if (namefile.indexOf(nregion) > 0){
        lstyears.forEach(function(nyear){     
            if (namefile.indexOf(nyear) > 0){   
                print("year " + yyear + " region " + yregion);
                var featmonth = ee.FeatureCollection(pathArea);
                var watertmp = layerWater.filter(ee.Filter.eq('cadence', 'annual'))
                                            .filter(ee.Filter.eq('year', parseInt(nyear)))
                                            .mosaic();  

                Map.addLayer(watertmp.select('classification'), vis.layerwater, 'water_' + yyear, false);
                Map.addLayer(featmonth, vis.areawater, yregion + "_" + yyear);
            }
        })
    }
    
})

var outline = ee.Image().byte().paint({
    featureCollection: regions,
    color: 1,
    width: 2
  });
Map.addLayer(outline, {palette: 'FF0000'}, 'edges');