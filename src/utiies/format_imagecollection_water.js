Map.setOptions('SATELLITE');
// Carrega a coleção original
var colecaoBruta = ee.ImageCollection('projects/nexgenmap/TRANSVERSAIS/AGUA5-FT')
  .filter(ee.Filter.eq('version', '11'))
  .filter(ee.Filter.eq('cadence', 'monthly'));

print('Coleção original:', colecaoBruta);
print('Total de imagens:', colecaoBruta.size());

// Lista de anos disponíveis
var anos = colecaoBruta.aggregate_array('year').distinct().sort();
print('Anos disponíveis:', anos);

// Função para gerar as imagens mensais mosaico por ano
var imagensMensais = anos.map(function(ano) {
    ano = ee.Number(ano).int();
    var imagensDoAno = colecaoBruta.filter(ee.Filter.eq('year', ano));
    var bandas = ee.Image(imagensDoAno.first()).bandNames();

    var imagensPorMes = bandas.map(function(nomeBanda) {
        var mes = ee.Number.parse(ee.String(nomeBanda).split('_').get(1)).int();
        var nomeFinal = ee.String('water_monthly_').cat(ano.format()).cat('_').cat(mes.format('%02d'));

        var imagemMensal = imagensDoAno.map(
            function(img) {
                    var banda = ee.Image(img).select([nomeBanda]);
                    return banda.multiply(ee.Image.constant(mes)).uint8();
                }).mosaic()
        .rename(nomeFinal)
        .set({
            'module': 'Water',
            'submodule': 'Water',
            'variable': 'Water Monthly',
            'format': 'temporal_categorical_singleband_collection',
            'version': '1', 
            'year': ano,
            'month': mes
        });

        return imagemMensal;
    });

    return imagensPorMes;
}).flatten();

var colecaoFinal = ee.ImageCollection.fromImages(imagensMensais);
print('Coleção final (nacional, mosaico por mês):', colecaoFinal);
print('Total de imagens mensais:', colecaoFinal.size());

// ===== UI para seleção de meses com cores =====
var mesesNomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
var paletaMeses = [
    '#E6F2FF', // Janeiro – azul quase branco
    '#CCE5FF', // Fevereiro
    '#B3D8FF', // Março
    '#99CCFF', // Abril
    '#80BFFF', // Maio
    '#66B2FF', // Junho
    '#4DA6FF', // Julho
    '#3399FF', // Agosto
    '#1A8CFF', // Setembro
    '#007FFF', // Outubro
    '#0066CC', // Novembro
    '#004080'  // Dezembro – azul escuro intenso
];

var checkboxPairs = mesesNomes.map(function(nome, i) {
    var checkbox = ui.Checkbox('', true);
    var label = ui.Label({
        value: nome,
        style: {
            backgroundColor: paletaMeses[i],
            padding: '2px 6px',
            margin: '2px',
            borderRadius: '4px',
            color: 'black',
            fontWeight: 'bold'
        }
    });
    return ui.Panel([checkbox, label], ui.Panel.Layout.Flow('horizontal'));
});

// Variável global para o ano selecionado (default 2020)
var anoSelecionado = 2020;

// Slider de seleção de ano
var sliderAno = ui.Slider({
    min: anos.get(0).getInfo(),
    max: anos.get(anos.length().subtract(1)).getInfo(),
    step: 1,
    value: anoSelecionado,
    style: {stretch: 'horizontal'},
    onChange: function(val) {
        anoSelecionado = val;
        labelAno.setValue('Ano: ' + val);
        atualizarVisualizacao();
    }
});
var labelAno = ui.Label('Ano: ' + anoSelecionado, {fontWeight: 'bold'});

// Botão de atualização
var botaoAtualizar = ui.Button('Atualizar visualização');

// Função para extrair meses ativos
function getMesesSelecionados() {
    return checkboxPairs
        .map(function(pair, i) {
            var cb = pair.widgets().get(0);
            return cb.getValue() ? i + 1 : null;
        })
        .filter(function(m) { return m !== null; });
}

// Função para atualizar visualização
function atualizarVisualizacao() {
    Map.layers().reset();

    var mesesSelecionados = getMesesSelecionados();
    if (mesesSelecionados.length === 0) {
        print('Nenhum mês selecionado.');
        return;
    }

    var colecaoFiltrada = anos.map(function(ano) {
        ano = ee.Number(ano).int();

        var imagens = colecaoFinal
        .filter(ee.Filter.eq('year', ano))
        .filter(ee.Filter.inList('month', mesesSelecionados));

        var imagemReduzida = imagens.map(function(img) {
                    return ee.Image(img).rename('water');
                }).reduce(ee.Reducer.max());

        return imagemReduzida
                .rename(ee.String('water_last_month_').cat(ano.format()))
                .set({
                    'year': ano,
                    'descricao': 'Último mês com água (meses selecionados)'
                });
    });

    var colecaoUI = ee.ImageCollection.fromImages(colecaoFiltrada);
    
    print("ver imagem modificada ", colecaoUI);

    // Visualiza o ano selecionado no slider
    var imagem = colecaoUI.filter(ee.Filter.eq('year', anoSelecionado)).first();

    Map.centerObject(geometry, 12);
    Map.addLayer(imagem, {
        min: 1,
        max: 12,
        palette: paletaMeses
    }, 'Água - último mês (' + anoSelecionado + ')');
}

// Liga botão ao atualizar
botaoAtualizar.onClick(atualizarVisualizacao);

// Painel lateral (superior esquerdo)
var painelUI = ui.Panel({
    widgets: [ui.Label('Selecione os meses ativos:')]
        .concat(checkboxPairs)
        .concat([botaoAtualizar]),
    style: {position: 'top-left'}
});
Map.add(painelUI);

var painelAno = ui.Panel({
    widgets: [labelAno, sliderAno],
    layout: ui.Panel.Layout.flow('horizontal'),
    style: {
        position: 'bottom-center',
        padding: '10px',
        backgroundColor: 'white',
        width: '620px',
        border: '1px solid #ccc',
        borderRadius: '8px'
    }
});
Map.add(painelAno);

// Visualização inicial
atualizarVisualizacao();