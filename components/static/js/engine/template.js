const templateUtil = {
    renderPropSection: function(prop){
        let { name, label, type, value } = prop;
        type = type || 'string';
        type = (type == 'int' || type == 'float') ? 'number' : type;
        return `<div class="form-group row">
                    <label for="${name}" class="col-4 col-form-label">${label}：</label>
                    <div class="col-8">
                        <input type="text" readonly class="form-control-plaintext" name="prop[${name}]:${type}" value="${value}">
                    </div>
                </div>`
    },
    renderParamSection: function(param) {
        let { name, label, value, defaultValue } = param;
        value = value || defaultValue;
        return `<div class="form-group row">
                    <label for="${name}" class="col-4 col-form-label">${label}：</label>
                    <div class="col-8">
                        <input type="text" id="${name}" name="param[${name}]" class="form-control" value="${value}" />
                    </div>
                </div>`
    },
    renderObjectFunc: function() {
        return `
            <div class="card border-primary objectFunc-section">
                <div class="card-header">
                    <div style="text-align: right; padding-right: 0px;">
                        <button type="button" id="objectFunc-delete" class="close" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                </div>
                <div class="card-body" style="padding-top: 32px; padding-right:32px">
                    <form class="objectFunc-form">
                        <div class="form-group row" style="margin-top: 10px;">
                        <label for="desc" class="col-4 col-form-label">优化目标描述：</label>
                        <input type="text" name="desc" class="col-8 form-control" placeholder="简单描述你的优化问题" />
                        </div>
                        <div class="form-group row">
                            <label for="" class="col-4 col-form-label">目标函数类型：</label>
                            <div class="col-8" style="padding-top: 7px;">
                                <div class="form-check form-check-inline">
                                    <input class="form-check-input" type="radio" name="type" value="vector" checked>
                                    <label class="form-check-label" for="param-type">参数形式</label>
                                </div>
                                <div class="form-check form-check-inline">
                                    <input class="form-check-input" type="radio" name="type" value="expression">
                                    <label class="form-check-label" for="formula-type">公式形式</label>
                                </div>
                            </div>
                        </div>
                        <div class="form-group row">
                            <label for="def" class="col-4 col-form-label col-form-label">目标函数定义：</label>
                            <input type="text" name="def" class="col-8 form-control form-control"/>
                        </div>
                    </form>
                </div>
            </div>
        `;
    },
    renderCustomizeParam: function() {
        return `
            <form class="customize-form">
                <div class="form-group row customize-row" id="customize">
                    <input type="text" name="key" class="form-control" placeholder="参数名称" required>
                    <input type="text" name="value" class="form-control" placeholder="参数值" required>
                    <div id="remove-customize">
                        <svg t="1615368564134" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4474" width="18" height="18"><path d="M516.096 84.65c236.773 0 428.715 191.943 428.715 428.715 0 236.773-191.942 428.715-428.715 428.715-236.773 0-428.715-191.942-428.715-428.715 0-236.772 191.942-428.714 428.715-428.714z m0 81.92c-191.53 0-346.795 155.266-346.795 346.795 0 191.53 155.266 346.795 346.795 346.795 191.53 0 346.795-155.265 346.795-346.795 0-191.53-155.266-346.794-346.795-346.794z m177.493 316.758c22.622 0 40.96 18.338 40.96 40.96s-18.338 40.96-40.96 40.96H338.603c-22.622 0-40.96-18.338-40.96-40.96s18.338-40.96 40.96-40.96h354.986z" fill="#2B313D" p-id="4475"></path></svg>
                    </div>
                </div>
            </form>
        `
    },
    renderCustomizeConstraint: function() {
        return `
            <form class="constraint-customize-form">
                <div class="form-group row customize-row" id="customize">
                    <input type="text" name="key" class="form-control" placeholder="约束名称" required>
                    <input type="text" name="value" class="form-control" placeholder="约束值" required>
                    <div id="remove-customize">
                        <svg t="1615368564134" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4474" width="18" height="18"><path d="M516.096 84.65c236.773 0 428.715 191.943 428.715 428.715 0 236.773-191.942 428.715-428.715 428.715-236.773 0-428.715-191.942-428.715-428.715 0-236.772 191.942-428.714 428.715-428.714z m0 81.92c-191.53 0-346.795 155.266-346.795 346.795 0 191.53 155.266 346.795 346.795 346.795 191.53 0 346.795-155.265 346.795-346.795 0-191.53-155.266-346.794-346.795-346.794z m177.493 316.758c22.622 0 40.96 18.338 40.96 40.96s-18.338 40.96-40.96 40.96H338.603c-22.622 0-40.96-18.338-40.96-40.96s18.338-40.96 40.96-40.96h354.986z" fill="#2B313D" p-id="4475"></path></svg>
                    </div>
                </div>
            </form>
        `
    }
};