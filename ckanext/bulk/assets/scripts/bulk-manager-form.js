ckan.module("bulk-manager-form", function () {
  "use strict";

  return {
    const: {
      filterBlock: ".filters-list",
      updateToBlock: ".update-to-fields",
      actionSelect: ".bulk-select-action select",
      entitySelect: ".bulk-select-entity select",
      submitBtn: ".bulk-submit-form-btn",
    },
    options: {},

    initialize() {
      $.proxyAll(this, /_/);

      this.managerForm = this.el.find("form");
      this.updateToBlock = $(this.const.updateToBlock);
      this.filterBlock = $(this.const.filterBlock);
      this.actionSelect = $(this.const.actionSelect);
      this.entitySelect = $(this.const.entitySelect);
      this.submitBtn = $(this.const.submitBtn);

      this.actionSelect.on("change", this._onActionSelectChange);
      this.entitySelect.on("change", this._onEntitySelectChange);
      this.submitBtn.on("click", this._onSubmitBtnClick);
      this.managerForm.on("change", this._onFormChange);

      // this.entityTS = new TomSelect(this.entitySelect, {
      //   // onDropdownOpen: this._onEntityDropdownOpen,
      //   onChange: this._onEntitySelectChange,
      // });

      // Add event listeners on dynamic elements
      $('body').on('click', '.btn-item-remove', this._onFilterItemRemove);

      // ON INIT

      this._onActionSelectChange();
    },

    /**
     * Toggle the update to block based on the selected action
     *
     * @param {Event} e
     */
    _onActionSelectChange() {
      this.updateToBlock.toggle(this.actionSelect.val() === "update");
    },

    _onEntityDropdownOpen(dropdown) {
      Swal.fire({
        title: "Do you want to save the changes?",
        showDenyButton: true,
        confirmButtonText: "Yes",
        denyButtonText: "No"
      }).then((result) => {
        if (result.isConfirmed) {
          // Allow to change entity type
        } else if (result.isDenied) {
          this.entityTS.clear(true);
        }
      });
    },

    _onEntitySelectChange() {
      this._clearFilters();
    },

    _clearFilters() {
      this.filterBlock.find("select").prop("selectedIndex", 0);
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
        const value = $(el).find(".bulk-value-input input").val();

        if (field && operator && value) {
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

      const data = {
        entity_type: this.entitySelect.val(),
        action: this.actionSelect.val(),
        filters: this._getFilters(),
      }

      if (!data.filters.length) {
        console.log("No filters");
        return;
      }

      this.sandbox.client.call(
        "POST",
        "bulk_get_entities_by_filters",
        data,
        (data) => {
          console.log(data);
          $(".bulk-info").html("Found " + data.result.count + " entities");
        },
        (resp) => {
          iziToast.error({ message: resp });
        }
      );
    }
  }
})
