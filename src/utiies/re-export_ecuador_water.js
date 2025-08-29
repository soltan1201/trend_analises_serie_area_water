
var asset_water = 'projects/mapbiomas-ecuador/assets/MAPBIOMAS-WATER/COLECCION3/ECUADOR/FINAL-ASSETS/water-surface-03'

function exportarImagem(imgU, nameAl){   
    var IdAsset = asset_water + nameAl    
    var optExp = {
        'image': imgU,
        'description': nameAl, 
        'assetId':IdAsset, 
        'pyramidingPolicy': {".default": "mode"},  
        'region': imgU.geometry(),
        'scale': 30,
        'maxPixels': 1e13 
    }
    Export.image.toAsset(optExp)   
    print ("salvando ... ! " , nameAl);
}

var colecaoBruta = ee.ImageCollection(asset_water);
var lst_idCod = colecaoBruta.reduceColumns(ee.Reducer.toList(), ['system:index']).get('list').getInfo();

var cc = 0;
lst_idCod.forEach(function(idCod){
    print(" #" + cc + "  >> " + idCod);
    var img_raster = ee.Image(colecaoBruta.filter(ee.Filter.eq('system:index', idCod)).first());
    img_raster = img_raster.gt(0).selfMask();
    img_raster = img_raster.set('version', 2);
    print(img_raster.bandNames());
    exportarImagem(img_raster, idCod + "_v1");
    cc += 1;
})