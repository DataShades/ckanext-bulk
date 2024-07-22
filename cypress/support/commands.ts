/// <reference types="cypress" />
// ***********************************************
// This example commands.ts shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
//
// declare global {
//   namespace Cypress {
//     interface Chainable {
//       login(email: string, password: string): Chainable<void>
//       drag(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       dismiss(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       visit(originalFn: CommandOriginalFn, url: string, options: Partial<VisitOptions>): Chainable<Element>
//     }
//   }
// }

/**
 * Login into CKAN as `user`.
 */
Cypress.Commands.add("login", (user: string = "admin") => {
    // `Cypress.session.clearAllSavedSessions()` will remove all stored
    // sessions. Usefull if you accidentally cached wrong response from the application
    cy.session(
        user,
        () => {
            cy.fixture("users").then((users) => {
                cy.visit("/user/login");
                cy.get("input[name=login]").type(user);
                cy.get("input[name=password]")
                    .type(users[user].password)
                    .type("{enter}");
                cy.get(".account .username").should("contain", user);
            });
        },
        { cacheAcrossSpecs: true },
    );
});

declare namespace Cypress {
    interface Chainable {
        /**
         * Login as a CKAN user.
         *
         * @param {string} user Name of the logged in user. Default to `admin`
         * @example
         *    cy.login()
         *    cy.login("normal_user")
         */
        login(user?: string): Chainable<void>;
    }
}
