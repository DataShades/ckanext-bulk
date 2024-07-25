ckan.module("tom-select", function () {

    return {
        options: {
            valueField: "value",
            labelField: "text",
            plugins: ['dropdown_input'],
            customRender: false,
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
