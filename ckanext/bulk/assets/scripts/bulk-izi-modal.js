/**
 * iziModal adapter.
 * https://izimodal.marcelodolza.com
 */
ckan.module("bulk-izi-modal", function ($) {
  return {
    options: {},

    initialize() {
      // stop execution if dependency is missing.
      if (typeof $.fn.iziModal === "undefined") {
        // reporting the source of the problem is always a good idea.
        console.error(
          "[bulk-izi-modal] iziModal library is not loaded",
        );
        return;
      }

      this.modal = this.$("[data-izi-modal]").iziModal(this.options);
      this.trigger = this.$("[data-izi-trigger]");

      this.trigger.on("click", () => this.modal.iziModal("open"));
    },
  };
});
