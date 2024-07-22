/**
 * SortableJS adapter.
 * https://sortablejs.github.io/Sortable/
 */
ckan.module("bulk-sortable", function () {
  return {
    options: {},

    initialize() {
      // stop execution if dependency is missing.
      if (typeof Sortable === "undefined") {
        // reporting the source of the problem is always a good idea.
        console.error(
          "[bulk-sortable] SortableJS library is not loaded",
        );
        return;
      }

      Sortable.create(this.el[0]);
    },
  };
});
