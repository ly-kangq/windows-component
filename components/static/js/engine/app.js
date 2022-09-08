
$.ajaxSetup({
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
});
// mitt is lightweight eventbus component exposed from js/mitt.js as global
var eventBus = mitt();
eventBus.on('modelSelected', (modelName) => {
    console.log(`${modelName} selected`);
    let selectedModel;
    for (let model of engineData.models) {
        if (model.name == modelName) {
            selectedModel = model;
            break;
        }
    }
    if (selectedModel) {
        renderModel(selectedModel, "#model-detail");
    }
});

eventBus.on('algoSelected', (algoName) => {
    console.log(`${algoName} selected`);
    let selectedAlgo;
    for (let algo of engineData.algos) {
        if (algo.name == algoName) {
            selectedAlgo = algo;
            break;
        }
    }
    if (selectedAlgo) {
        renderAlgo(selectedAlgo, "#algo-detail");
    }
});

function renderConfigurationForm(modelOrAlgo, renderAt, descLabel) {
    let descHtml = `
        <div class="form-group row">
            <label for="modelDesc" class="col-4 col-form-label col-form-label">${descLabel}：</label>
            <div class="col-8">
                <input type="text" readonly class="form-control-plaintext" id="modelDesc" value="${modelOrAlgo.desc}">
            </div>
        </div>
    `;
    let propsHtml = '';
    for (let prop of modelOrAlgo.prop) {
        propsHtml += templateUtil.renderPropSection(prop);
    }
    let paramHtml = '';
    for (let param of modelOrAlgo.param) {
        paramHtml += templateUtil.renderParamSection(param);
    }
    $(renderAt).empty().append(descHtml + propsHtml + paramHtml);
}

function renderModel(model, selector) {
    renderConfigurationForm(model, selector, '模型描述');
}

function renderAlgo(algo, selector) {
    renderConfigurationForm(algo, selector, '算法描述');
}

function addObjectFunc() {
    $('#objectFuncList').append(templateUtil.renderObjectFunc());
}

function addCustomizeParam() {
    $('#output-customize-forms').append(templateUtil.renderCustomizeParam());
}

function addCustomizeConstraint() {
    $('#constraint-customize-forms').append(templateUtil.renderCustomizeConstraint());
}

function serializeAllConfigs() {
    try {
        let modelConfig = $('form#model-config-form').serializeJSON();
        let algoConfig = $('form#algo-config-form').serializeJSON();
        let objectFuncConfig = [];
        $('form.objectFunc-form').each(function() {
            objectFuncConfig.push($(this).serializeJSON());
        });
        let constraintConfig = {};
        $('form.constraint-form').each(function() {
            Object.assign(constraintConfig, $(this).serializeJSON());
        });
        let customizedConstraints = serializeCustomizedConstraint();
        constraintConfig.extra = customizedConstraints;
        let outputConfig = $('#output-defaultSetting-form').serializeJSON();
        outputConfig.param = serializeOutputConfigParam();
        let allConfigs = { modelConfig, algoConfig, objectFuncConfig, constraintConfig, outputConfig};
        $.post('api/v1/config', JSON.stringify(allConfigs), function(data) {
            if(data.success) {
                toastr.info('配置保存成功');
            } else {
                toastr.error(data.message, '配置保存失败');
            }
        }).fail(function(xhr, status, error) {
            toastr.error(error, '配置保存失败');
        });
    } catch(e) {
        console.error(e);
        toastr.error(e.message, '保存配置错误');
    }
}

function serializeOutputConfigParam() {
    let customizeConfig = {};
    $('form.customize-form').each(function() {
        const { key, value } = $(this).serializeJSON();
        if ( key !== '') {
            Object.assign(customizeConfig, { [key]: value });
        }
    });
    return customizeConfig;
}

function serializeCustomizedConstraint() {
    let custmizedConstraints = {};
    $('form.constraint-customize-form').each(function() {
        const { key, value } = $(this).serializeJSON();
        if ( key !== '') {
            Object.assign(custmizedConstraints, { [key]: value });
        }
    });
    return custmizedConstraints;
}

$(function () {
    $(".tab").on('click', function () {
        $("a.nav-link").removeClass("active");
        $(this).addClass("active");
    });
    $("#modelName").on('change', function () {
        eventBus.emit('modelSelected', $(this).val());
    });
    $("#algoName").on('change', function () {
        eventBus.emit('algoSelected', $(this).val());
    });
    $('#objectFunc-add').on('click', function () {
        addObjectFunc();
    });
    $('#objectFunc-save').on('click', function() {
        serializeAllConfigs();
    });
    $('#objectFuncList').on('click', function (e) {
        if($(e.target).parent().attr('id') == 'objectFunc-delete') {
            $(e.target).closest('.card').remove();
        }
    });
    $('#addCustomizeBtn').on('click', function() {
        addCustomizeParam();
    });
    $('#output-customize-forms').on('click', function (e) {
        if($(e.target).is('svg') && $(e.target).parent().attr('id') == 'remove-customize' ) {
            $(e.target).closest('.customize-form').remove();
        }
        if($(e.target).is('path') && $(e.target).parent().parent().attr('id') == 'remove-customize' ) {
            $(e.target).closest('.customize-form').remove();
        }
    });
    $('#saveCustomizeBtn').on('click', function() {
        serializeAllConfigs();
    });
    $('#addCustomizeConstraintBtn').on('click', function() {
        addCustomizeConstraint();
    });
    $('#constraint-customize-forms').on('click', function (e) {
        if($(e.target).is('svg') && $(e.target).parent().attr('id') == 'remove-customize' ) {
            $(e.target).closest('.constraint-customize-form').remove();
        }
        if($(e.target).is('path') && $(e.target).parent().parent().attr('id') == 'remove-customize' ) {
            $(e.target).closest('.constraint-customize-form').remove();
        }
    });
    $('#saveCustomizeConstraintBtn').on('click', function() {
        serializeAllConfigs();
    });
    $('form').on('submit', function (e) {
        e.preventDefault();
        serializeAllConfigs();
        return false;
    });
});