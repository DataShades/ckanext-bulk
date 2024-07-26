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
            bulkModalResult: "#bulk-modal-result",
            bulkModalLogs: "#bulk-modal-logs",
        },
        htmx: {
            addFilter: "/bulk/htmx/create_filter_item",
            addUpdate: "/bulk/htmx/create_update_item",
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
            this.bulkModalResult = $(this.const.bulkModalResult);
            this.bulkModalLogs = $(this.const.bulkModalLogs);

            this.actionSelect.on("change", this._onActionSelectChange);
            this.entitySelect.on("change", this._onEntitySelectChange);
            this.submitBtn.on("click", this._onSubmitBtnClick);
            this.managerForm.on("change", this._onFormChange);

            // Add event listeners on dynamic elements
            $('body').on('click', '.btn-item-remove', this._onFilterItemRemove);

            // initialize CKAN modules for HTMX loaded pages
            htmx.on("htmx:afterSettle", this._HTMXAfterSettle);

            // ON INIT
            this.bulkEntitiesToUpdate = [];
            this.bulkLogs = [];

            this._onActionSelectChange();
            this._initFieldSelectors(this.filterBlock.find(".bulk-field-select select"));
            this._initFieldSelectors(this.updateToBlock.find("select"));

            this.bulkModalResult.iziModal({
                title: 'Filtered entities',
                subtitle: 'A list of entities, that will be changed',
                padding: 20,
                radius: 3,
                borderBottom: false,
                width: 1000,
            });

            this.bulkModalLogs.iziModal({
                title: 'Logs',
                subtitle: 'Logs of the bulk update process',
                padding: 20,
                radius: 3,
                borderBottom: false,
                width: 1000,
            });
        },

        /**
         * This event is triggered after the DOM has settled.
         *
         * @param {Event} event
         */
        _HTMXAfterSettle(event) {
            if (event.detail.pathInfo.requestPath == this.htmx.addFilter) {
                this._initFieldSelectors(this.filterBlock.find(".bulk-field-select select"));
            } else if (event.detail.pathInfo.requestPath == this.htmx.addUpdate) {
                this._initFieldSelectors(this.updateToBlock.find("select"));
            }
        },

        /**
         * Toggle the update to block based on the selected action
         *
         * @param {Event} e
         */
        _onActionSelectChange() {
            this.updateToBlock.toggle(this.actionSelect.val() === "update");
        },

        /**
         * Triggers when user tries to change the entity type.
         *
         * Suggest user to clear the filters, because different entities might
         * have different fields.
         *
         * @param {Event} e
         */
        _onEntitySelectChange(e) {
            this._initFieldSelectors(this.filterBlock.find(".bulk-field-select select"), true);
            this._initFieldSelectors(this.updateToBlock.find("select"), true);

            if (!this._getFilters().length) {
                return;
            }

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

        /**
         * Clear all filters
         */
        _clearFilters() {
            this.filterBlock.find("select").get(0).tomselect.clear();
            this.filterBlock.find("input").val("");
            this.filterBlock.find(".bulk-fieldset-item:not(:first)").remove();
        },

        /**
         * Clear all update fields. For now we're not using it.
         */
        _clearUpdateOn() {
            this.updateToBlock.find("select").get(0).tomselect.clear();
            this.updateToBlock.find("input").val("");
            this.updateToBlock.find(".bulk-fieldset-item:not(:first)").remove();
        },

        /**
         * Triggers when user tries to remove a filter item.
         *
         * If there is only one item left, show an error message and do not allow
         * to remove it.
         *
         * If the item is removed, trigger the change event on the form, to recalculate
         * the number of entities that will be updated.
         *
         * @param {Event} e
         */
        _onFilterItemRemove(e) {
            if ($(e.target).closest(".bulk-list").find(".bulk-fieldset-item").length <= 1) {
                iziToast.error({ message: "You can't remove the last item" });
                return;
            };

            $(e.target).closest(".bulk-fieldset-item").remove();

            this.managerForm.trigger("change");
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
            const data = {
                entity_type: this.entitySelect.val(),
                action: this.actionSelect.val(),
                filters: this._getFilters(),
                global_operator: this.globalOperator.is(":checked") ? "AND" : "OR",
            }

            this._toggleLoadSpinner(true);
            // window.bulkUpdateOn = this._getUpdateOn();

            if (!data.filters.length) {
                this.infoBlock.find(".counter").html("There will be information about how many entities will be changed.");
                return this._toggleLoadSpinner(false);
            }

            this.sandbox.client.call(
                "POST",
                "bulk_get_entities_by_filters",
                data,
                (data) => {
                    if (!data.result || data.result.error || data.result.fields.length === 0) {
                        if (data.result.error) {
                            iziToast.error({ message: data.result.error });
                        }

                        this.bulkModalResult.iziModal('setContent', "<p>No results yet</p>");
                        this.infoBlock.find(".counter").html("Found 0 entities");
                        this.bulkEntitiesToUpdate = [];
                        return this._toggleLoadSpinner(false);
                    }

                    this.bulkModalResult.iziModal(
                        "setContent",
                        "<pre class='language-javascript'>"
                        + JSON.stringify(data.result.fields, null, 2)
                        + "</pre>"
                    );

                    Prism.highlightElement(this.bulkModalResult.find("pre")[0]);

                    this.bulkEntitiesToUpdate = data.result.fields;
                    this.infoBlock.find(".counter").html("Found " + data.result.fields.length + " entities");
                    this._toggleLoadSpinner(false);
                },
                (resp) => {
                    iziToast.error({ message: resp });
                    this._toggleLoadSpinner(false);
                }
            );
        },

        _initFieldSelectors: function (selectItems, reinit = false) {
            let prevValue = "";

            selectItems.each((_, el) => {
                if (el.tomselect !== undefined) {
                    if (reinit) {
                        prevValue = el.tomselect.getValue();
                        el.tomselect.destroy();
                    } else {
                        return;
                    }
                }

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
                    onInitialize: function () {
                        if (prevValue) {
                            this.input.tomselect.addOption({
                                text: prevValue,
                                value: prevValue,
                            });
                            this.input.tomselect.setValue(prevValue);
                        };
                    }
                });
            });
        },

        _toggleLoadSpinner: function (show) {
            this.infoBlock.find(".spinner").toggle(show);
        },

        _onSubmitBtnClick: async function (e) {
            const entity_type = this.entitySelect.val();
            const action = this.actionSelect.val();
            const update_on = this._getUpdateOn();

            if (!this.bulkEntitiesToUpdate.length) {
                iziToast.error({ message: "Please, check the filters first" });
                return;
            }

            if (!update_on.length) {
                iziToast.error({ message: "Please, fill the update fields" });
                return;
            }

            const bulkProgressBar = this._initProgressBar();

            for (let i = 0; i < this.bulkEntitiesToUpdate.length; i++) {
                const entity = this.bulkEntitiesToUpdate[i];

                try {
                    await this._callUpdateEntity(entity, entity_type, update_on, action);
                    bulkProgressBar.animate(
                        bulkProgressBar.value() + 1 / this.bulkEntitiesToUpdate.length
                    );
                } catch (error) {
                    iziToast.error({ message: error });
                }
            };

            bulkProgressBar.destroy();

            iziToast.success({ message: "Bulk operation is finished. Check the logs to see results" });
        },

        _initProgressBar: function () {
            const bulkProgressBar = new ProgressBar.Line($("#bulk-progress-container").get(0), {
                strokeWidth: 4,
                easing: 'easeInOut',
                duration: 1400,
                color: '#206b82',
                trailColor: '#EEE',
                trailWidth: 1,
                svgStyle: { width: '100%', height: '100%' },
                text: {
                    style: {
                        position: 'absolute',
                        left: '0',
                        top: '30px',
                    },
                    autoStyleContainer: false
                },
                step: (_, bar) => {
                    bar.setText(Math.round(bar.value() * 100) + ' %');
                }
            });

            bulkProgressBar.animate(0);

            return bulkProgressBar;
        },

        _callUpdateEntity: function (entity, entity_type, update_on, action) {
            return new Promise((done, fail) => {
                this.sandbox.client.call("POST", "bulk_update_entity", {
                    entity_type: entity_type,
                    entity_id: entity.id,
                    update_on: update_on,
                    action: action,
                }, (resp) => {
                    this.bulkLogs.push(resp.result);

                    this.bulkModalLogs.iziModal(
                        "setContent",
                        {
                            content: "<pre class='language-javascript'>"
                                + JSON.stringify(this.bulkLogs, null, 2)
                                + "</pre>",
                        }
                    );
                    done(resp);
                }, (resp) => {
                    fail(resp)
                });
            });
        }
    }
})
