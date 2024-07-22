/**
 * Cypress configuration file: https://docs.cypress.io/guides/references/configuration
 */
import { defineConfig } from "cypress";

export default defineConfig({
    e2e: {
        // URL prefix for cy.visit() and cy.request()
        baseUrl: "http://localhost:5000",
    },
});
