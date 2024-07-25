ckan.module("bulk-manager-form", function () {
    "use strict";

    return {
        const: {
            filterBlock: ".filters-list",
            updateToBlock: ".update-to-fields",
            actionSelect: ".bulk-select-action select",
            entitySelect: ".bulk-select-entity select",
            submitBtn: ".bulk-submit-form-btn",
            globalOperator: "#global_operator",
            infoBlock: ".bulk-info",
        },
        options: {},

        initialize() {
            $.proxyAll(this, /_/);

            this.managerForm = this.el.find("form");
            this.filterBlock = $(this.const.filterBlock);
            this.updateToBlock = $(this.const.updateToBlock);
            this.actionSelect = $(this.const.actionSelect);
            this.entitySelect = $(this.const.entitySelect);
            this.submitBtn = $(this.const.submitBtn);
            this.globalOperator = $(this.const.globalOperator);
            this.infoBlock = $(this.const.infoBlock);

            this.actionSelect.on("change", this._onActionSelectChange);
            this.entitySelect.on("change", this._onEntitySelectChange);
            this.submitBtn.on("click", this._onSubmitBtnClick);
            this.managerForm.on("change", this._onFormChange);

            // Add event listeners on dynamic elements
            $('body').on('click', '.btn-item-remove', this._onFilterItemRemove);

            // initialize CKAN modules for HTMX loaded pages
            htmx.on("htmx:afterSettle", this._HTMXAfterSettle);

            // ON INIT
            this._onActionSelectChange();

            this._initFieldSelectors(this.filterBlock.find(".bulk-field-select select"));
            this._initFieldSelectors(this.updateToBlock.find("select"));
            this._toggleRemoveBtns();
        },

        _HTMXAfterSettle(event) {
            if (event.detail.pathInfo.requestPath == "/bulk/create_filter_item") {
                this._initFieldSelectors(this.filterBlock.find(".bulk-field-select select"));
            } else if (event.detail.pathInfo.requestPath == "/bulk/create_update_item") {
                this._initFieldSelectors(this.updateToBlock.find("select"));
            }

            this._toggleRemoveBtns();
        },

        /**
         * Toggle the update to block based on the selected action
         *
         * @param {Event} e
         */
        _onActionSelectChange() {
            this.updateToBlock.toggle(this.actionSelect.val() === "update");
        },

        _onEntitySelectChange(e) {
            if (!this._getFilters().length) {
                return;
            }

            this._reinitFieldSelectors(this.filterBlock.find(".bulk-field-select select"));
            this._reinitFieldSelectors(this.updateToBlock.find("select"));

            // HACK: select an input because swal will focus the last focused element
            // and we don't want it to be an entity selector
            $("#value").get(0).focus()

            Swal.fire({
                title: "Do you want to clear the filters?",
                showDenyButton: true,
                confirmButtonText: "Yes",
                denyButtonText: "No"
            }).then((result) => {
                if (result.isConfirmed) {
                    this._clearFilters();
                }
            });
        },

        _clearFilters() {
            this.filterBlock.find("select").get(0).tomselect.clear();
            this.filterBlock.find("input").val("");
            this.filterBlock.find(".filter-item:not(:first)").remove();
            this.filterBlock.find(".filter-item .btn").prop("disabled", "disabled");
        },

        _clearUpdateOn() {
            this.updateToBlock.find("select").prop("selectedIndex", 0);
            this.updateToBlock.find("input").val("");
            this.updateToBlock.find(".update-field-item:not(:first)").remove();
            this.updateToBlock.find(".update-field-item .btn").prop("disabled", "disabled");
        },

        _onFilterItemRemove(e) {
            $(e.target).closest(".bulk-fieldset-item").remove();

            this.managerForm.trigger("change");

            this._toggleRemoveBtns();
        },

        _toggleRemoveBtns() {
            if (this.filterBlock.find(".bulk-fieldset-item").length == 1) {
                this.filterBlock.find(".filter-item .btn").prop("disabled", "disabled");
            } else {
                this.filterBlock.find(".filter-item .btn").prop("disabled", false);
            }

            if (this.updateToBlock.find(".update-field-item").length == 1) {
                this.updateToBlock.find(".update-field-item .btn").prop("disabled", "disabled");
            } else {
                this.updateToBlock.find(".update-field-item .btn").prop("disabled", false);
            }
        },

        _onSubmitBtnClick(e) {
            const data = {
                entity_type: this.entitySelect.val(),
                action: this.actionSelect.val(),
                filters: this._getFilters(),
                update_on: this._getUpdateOn(),
            }

            console.log(data);

            this.sandbox.client.call(
                "POST",
                "bulk_perform",
                data,
                (data) => {
                    //
                },
                (resp) => {
                    iziToast.error({ message: resp });
                }
            );
        },

        _getFilters() {
            const filters = [];

            this.filterBlock.find(".filter-item").each((_, el) => {
                const field = $(el).find(".bulk-field-select select").val();
                const operator = $(el).find(".bulk-operator-select select").val();
                const value = $(el).find(".bulk-value-input input").val() || "";

                if (field && operator) {
                    filters.push({ field, operator, value });
                }
            });

            return filters;
        },

        _getUpdateOn() {
            const updateOn = [];

            this.updateToBlock.find(".update-field-item").each((_, el) => {
                const field = $(el).find("#update_field").val();
                const value = $(el).find("#update_value").val();

                if (field && value) {
                    updateOn.push({ field, value });
                }
            });

            return updateOn;
        },

        _onFormChange() {
            console.log("Form changed");
            console.log(this.globalOperator);

            const data = {
                entity_type: this.entitySelect.val(),
                action: this.actionSelect.val(),
                filters: this._getFilters(),
                global_operator: this.globalOperator.is(":checked") ? "AND" : "OR",
            }

            this._toggleLoadSpinner(true);

            if (!data.filters.length) {
                this.infoBlock.find(".counter").html("There will be information about how many entities will be changed.");
                return this._toggleLoadSpinner(false);
            }

            this.sandbox.client.call(
                "POST",
                "bulk_get_entities_by_filters",
                data,
                (data) => {
                    console.log(data);
                    this.infoBlock.find(".counter").html("Found " + data.result.length + " entities");
                    this._toggleLoadSpinner(false);
                },
                (resp) => {
                    iziToast.error({ message: resp });
                    this._toggleLoadSpinner(false);
                }
            );
        },

        _initFieldSelectors: function (selectItems, reinit = false) {
            selectItems.each((_, el) => {
                if (el.tomselect !== undefined) {
                    if (reinit) {
                        el.tomselect.destroy();
                    } else {
                        return;
                    }
                }

                console.log(el);

                const self = this;

                new TomSelect(el, {
                    valueField: "value",
                    labelField: "text",
                    plugins: ['dropdown_input'],
                    placeholder: "Search for field name",
                    create: true,
                    preload: true,
                    load: function (query, callback) {
                        var url = `/api/action/bulk_search_fields?query=${encodeURIComponent(query)}&entity_type=${self.entitySelect.val()}`;
                        fetch(url)
                            .then(response => response.json())
                            .then(json => {
                                callback(json.result);
                            }).catch(() => {
                                callback();
                            });
                    },
                });
            });
        },

        _toggleLoadSpinner: function (show) {
            this.infoBlock.find(".spinner").toggle(show);
        }
    }
})
