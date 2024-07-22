/**
 * Tests for bulk-swal module.
 */

// main CKAN JS entrypoint
const ckan = () => cy.window({ log: false }).then((win) => win["ckan"]);

// Prepare button element. It's not initialized because you may need extra
// parameters added to it before initialization.
const makeButton = () =>
    cy.window({ log: false }).then((win) => {
        return win
            .jQuery(
                "<button data-module='bulk-swal'>Fixture</button>",
            )
            .appendTo(win.document.body);
    });

// initialize CKAN JS modules of the element
const init = (el) =>
    ckan().then((ckan) => {
        ckan.module.initializeElement(el[0]);
        return el;
    });

// Switch to page that does not contain any interferring JS
beforeEach(() => {
    cy.visit("/about");
});

// `describe` is used to group tests by feature
describe("Swal module", () => {

    // Every `it` is a test. Do something inside `it` and make assertions in
    // the end.
    it("shows allert", () => {
        // initialize the simples swal module
        const btn = makeButton().then(init);

        const modal = ".swal2-modal";

        // verify that modal is not yet shown
        cy.get(modal).should("not.exist");

        // toggle the modal
        btn.click();

        // verify that modal is visible, then find element with OK label(button
        // inside the modal) and click on it.
        cy.get(modal).should("be.visible").contains("OK").click();

        // modal must disappear after clicking the OK button
        cy.get(modal).should("not.exist");
    });

    it("can be configured", () => {
        const title = "hello world!";

        // modify swal configuration before initializing the module
        const btn = makeButton().then((btn) =>
            init(btn.attr("data-module-title", title)),
        );

        cy.contains(title).should("not.exist");
        btn.click();

        // check presence of the modal with expected content
        cy.contains(title).should("be.visible");
    });
});
