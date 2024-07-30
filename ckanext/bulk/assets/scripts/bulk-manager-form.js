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
            bulkResultContainer: "#bulk-result-container",
            bulkLogsContainer: "#bulk-logs-container",
        },
        htmx: {
            addFilter: "/bulk/htmx/create_filter_item",
            addUpdate: "/bulk/htmx/create_update_item",
        },
        options: {
            resultMaxEntries: 50,
            logsMaxEntries: 50,
        },

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
            this.bulkResultContainer = $(this.const.bulkResultContainer);
            this.bulkLogsContainer = $(this.const.bulkLogsContainer);

            this.actionSelect.on("change", this._onActionSelectChange);
            this.entitySelect.on("change", this._onEntitySelectChange);
            this.submitBtn.on("click", this._onSubmitBtnClick);
            this.managerForm.on("change", this._onFormChange);

            window.onbeforeunload = function (_) {
                return "Are you sure you want to leave this page? The bulk action is in progress.";
            };

            // global setup for toast messages
            this.toast = Swal.mixin({
                toast: true,
                position: "bottom-end",
                showConfirmButton: false,
                showCloseButton: true,
                timer: 3000,
                timerProgressBar: true,
                didOpen: (toast) => {
                    toast.onmouseenter = Swal.stopTimer;
                    toast.onmouseleave = Swal.resumeTimer;
                }
            });

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
                return this.toast.fire({
                    icon: "error",
                    title: "You can't remove the last item"
                });
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

        _onFormChange(e) {
            // if update item is changing, do not trigger the form change
            if ($(e.target).closest(".update-field-item").length) {
                e.preventDefault();
                return;
            }

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
                    if (!data.result || data.result.error || data.result.entities.length === 0) {
                        if (data.result.error) {
                            this._toggleLoadSpinner(false);

                            return this.toast.fire({
                                icon: "error",
                                title: data.result.error
                            });
                        }

                        this.bulkResultContainer.html("<p>No results yet</p>");
                        this.infoBlock.find(".counter").html("Found 0 entities");
                        this.bulkEntitiesToUpdate = [];

                        this.toast.fire({
                            icon: "success",
                            title: "Found 0 entities"
                        });

                        return this._toggleLoadSpinner(false);
                    }

                    this.bulkResultContainer.html($(`
                        <p>Showing first ${this.options.resultMaxEntries} entities</p>
                        <pre class='language-javascript'>
                            ${JSON.stringify(this._limitResultEntries(data.result.entities), null, 2)}
                        </pre>
                    `)).promise().done(() => {
                        Prism.highlightElement(this.bulkResultContainer.find("pre")[0]);

                        this.bulkEntitiesToUpdate = data.result.entities;
                        this.infoBlock.find(".counter").html("Found " + data.result.entities.length + " entities");

                        this.toast.fire({
                            icon: "success",
                            title: `Found ${data.result.entities.length} entities`
                        });

                        this._toggleLoadSpinner(false);
                    });
                },
                (resp) => {
                    this.toast.fire({
                        icon: "error",
                        title: resp
                    });
                    this._toggleLoadSpinner(false);
                }
            );
        },

        /**
         * Limit the number of entries in the result to avoid performance issues.
         *
         * Also remove some fields that are not needed for the user.
         *
         * @param {Array<Object>} entities
         *
         * @returns {Array<Object>}
         */
        _limitResultEntries: function (entities) {
            entities = entities.slice(0, this.options.resultMaxEntries);

            entities.forEach(entity => {
                delete entity.resources;
                delete entity.organization;
                delete entity.groups;

                delete entity.relationships_as_subject,
                    delete entity.relationships_as_object;
            });

            return entities;
        },

        /**
         * Limit the number of entries in the logs to avoid performance issues.
         *
         * Also remove some fields that are not needed for the user.
         *
         * @param {Array<Object>} logs
         *
         * @returns {Array<Object>}
         */
        _limitLogsEntries: function (logs) {
            logs = logs.slice(logs.length - this.options.logsMaxEntries, logs.length);

            logs.forEach(log => {
                if (!log.result) {
                    return;
                }

                delete log.result.resources;
                delete log.result.organization;
                delete log.result.groups;

                delete log.result.relationships_as_subject,
                    delete log.result.relationships_as_object;
            });

            return logs;
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
                            this.input.tomselect.setValue(prevValue, true);
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
                return this.toast.fire({
                    icon: "error",
                    title: "Please, check the filters first"
                });
            }

            if (this.updateToBlock.is(":visible") && !update_on.length) {
                return this.toast.fire({
                    icon: "error",
                    title: "Please, fill the update fields"
                });
            }

            this.bulkProgressBar = this._initProgressBar();

            for (let i = 0; i < this.bulkEntitiesToUpdate.length; i++) {
                const entity = this.bulkEntitiesToUpdate[i];

                try {
                    await this._callUpdateEntity(entity, entity_type, update_on, action);
                    this.bulkProgressBar.animate(
                        this.bulkProgressBar.value() + this.bulkProgressBarPercent
                    );
                } catch (error) {
                    this.toast.fire({
                        icon: "error",
                        title: error
                    });
                }
            };

            this.bulkProgressBar.destroy();

            this.toast.fire({
                icon: "success",
                title: "Bulk operation is finished. Check the logs to see results"
            });

            this.bulkLogsContainer.html(`
                <p>Showing last ${this.options.logsMaxEntries} entries</p>
                <pre class='language-javascript'>
                    ${JSON.stringify(this._limitLogsEntries(this.bulkLogs), null, 2)}
                </pre>
            `).promise().done(() => {
                Prism.highlightElement(this.bulkLogsContainer.find("pre")[0]);
            });
        },

        _initProgressBar: function () {
            const bulkProgressBar = new BulkProgressBar("#bulk-progress-container", {});

            bulkProgressBar.animate(0);

            this.bulkProgressBarPercent = 100 / this.bulkEntitiesToUpdate.length;

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

                    done(resp);
                }, (resp) => {
                    fail(resp)
                });
            });
        }
    }
})

class BulkProgressBar {
    /**
     * Create a new progress bar instance inside a container
     *
     * @param {String} container - container selector
     * @param {Object} options - progress bar options
     */
    constructor(container, options) {
        this.container = $(container);

        if (!this.container) {
            throw new Error("Container not found");
        }

        this.options = options;
        this.progress = 0;

        this.container.addClass("bulk-progress-bar");
        this.container.append(`
            <div id='pb-runner-wrapper'>
                <div id='pb-runner'></div>
            </div>
        `);
        this.container.append("<div id='pb-status'></div>");
    }

    /**
     * Animate the progress bar
     *
     * @param {Number} value - progress value from 0 to 100
     */
    animate(value) {
        value = Math.round(value * 100) / 100;

        if (value > 100) {
            value = 100;
        }

        this.progress = value;

        this.container.find("#pb-runner").width(`${value}%`);
        this.container.find("#pb-status").html(`${value}%`);
    }

    /**
     * Get current progress value
     *
     * @returns {Number} - current progress value
     */
    value() {
        return this.progress;
    }

    /**
     * Destroy the progress bar inside a container
     */
    destroy() {
        this.container.removeClass("bulk-progress-bar");
        this.container.empty();
    }
}
