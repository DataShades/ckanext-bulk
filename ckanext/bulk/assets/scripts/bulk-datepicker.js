/**
 * Daterangepicker adapter.
 * https://www.daterangepicker.com/
 */
ckan.module("bulk-datepicker", function ($) {
  return {
    options: {},

    initialize() {
      // stop execution if dependency is missing.
      if (typeof $.fn.daterangepicker === "undefined") {
        // reporting the source of the problem is always a good idea.
        console.error(
          "[bulk-datepicker] daterangepicker library is not loaded",
        );
        return;
      }

      const options = this.sandbox["bulk"].nestedOptions(
        this.options,
      );

      this.el.daterangepicker(options);
    },
  };
});
