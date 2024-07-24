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
            valueField: 'label',
            labelField: 'label',
            plugins: ['dropdown_input'],
            load: function (query, callback) {
                var url = 'https://api.github.com/search/repositories?q=' + encodeURIComponent(query);
                fetch(url)
                    .then(response => response.json())
                    .then(json => {
                        callback(json.items);
                    }).catch(() => {
                        callback();
                    });
            },
            render: {
                option: function (item, escape) {
                    console.log(item);
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
            },
        },

        initialize() {
            // stop execution if dependency is missing.
            if (typeof TomSelect === "undefined") {
                // reporting the source of the problem is always a good idea.
                console.error("[bulk-tom-select] TomSelect library is not loaded");
                return
            }

            // tom-select has a number of nested options. We are using
            // `nestedOptions` helper defined inside `bulk.js` to
            // convert flat options of CKAN JS module into nested object.
            const options = this.sandbox["bulk"].nestedOptions(this.options);

            // in this case there is no value in keeping the reference to the
            // widget. But if you are going to extend this module, sharing
            // information between methods through `this` is a good choice.
            if (this.el.get(0, {}).tomselect) {
                return;
            }

            this.widget = new TomSelect(this.el, options);
        }
    }
})
