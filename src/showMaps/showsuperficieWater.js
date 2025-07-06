var vis = {
    water: {
        min: 0, max: 1,
        palette: '0000FF'
    }
}
// var asset_sup_water = 'projects/mapbiomas-workspace/TRANSVERSAIS/AGUA5-FT';
var asset_sup_water = 'projects/mapbiomas-peru/assets/WATER/COLLECTION-3/FINAL-ASSETS/water-surface-01';

var col = ee.ImageCollection(asset_sup_water)
                   .filter(ee.Filter.eq('version', 1.0))
print("show the versions ", col.aggregate_histogram('version'));
print("show metadatos da colection", col);

var water_yy = col.filter(ee.Filter.eq('year', 1985))
                  .filter(ee.Filter.eq('frequency', 'annual'))
                  .first();
Map.addLayer(water_yy, vis.water, '1985');