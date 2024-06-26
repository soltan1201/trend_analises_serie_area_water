var col = ee.ImageCollection('projects/mapbiomas-workspace/TRANSVERSAIS/AGUA5-FT')
  .filter(ee.Filter.eq('version', '11'))
  
print(col)