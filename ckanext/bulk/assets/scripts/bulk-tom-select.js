/**
 * TomSelect adapter.
 * https://tom-select.js.org/
 */
ckan.module("tom-select", function () {

    return {
        // any attribute with `data-module-` prefix transforms into camelized
        // option. `data-module-hello-world="1"` becomes `helloWorld: 1`. Case
        // transformation happens only after hyphen. This is used to pass nested
        // options. For example, `data-module-hello-world_bye-world` becomes
        // `helloWorld_byeWorld`. Then options are processed by
        // `this.sandbox.bulk.nestedOptions` and we receive
        // `{helloWorld: {byeWorld: ...}}`.
        options: {
            valueField: 'value',
            labelField: 'text',
            plugins: ['dropdown_input'],
            customRender: false,
            load: function (query, callback) {
                var url = '/api/action/bulk_search_fields?query=' + encodeURIComponent(query) + "&entity_type=dataset";
                fetch(url)
                    .then(response => response.json())
                    .then(json => {
                        callback(json.result);
                    }).catch(() => {
                        callback();
                    });
            },
            render: {},
        },

        initialize() {
            if (typeof TomSelect === "undefined") {
                console.error("[bulk-tom-select] TomSelect library is not loaded");
                return
            }

            if (this.options.customRender) {
                this.options.render.option = function (item, escape) {
                    return `
                    <div class="py-2 d-flex">
                        <div class="mb-1">
                            <span class="h5">
                                ${escape(item.text)}
                            </span>
                        </div>
                        <div class="ms-auto">${escape(item.value)}</div>
                    </div>
                    `;
                }
            }

            const options = this.sandbox["bulk"].nestedOptions(this.options);

            if (this.el.get(0, {}).tomselect) {
                return;
            }

            this.widget = new TomSelect(this.el, options);
        }
    }
})
