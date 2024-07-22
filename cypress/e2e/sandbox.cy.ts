/**
 * Tests for additional sandbox functionality
 */

// main CKAN JS entrypoint
const ckan = () => cy.window({ log: false }).then((win) => win["ckan"]);

// Instance of the sandbox
const sandbox = () => ckan().invoke({ log: false }, "sandbox");

// Example of mocking API request. Mocked request is available via
// `cy.get("@request")`
// const intercept = (
//     action: string,
//     alias: string = "request",
//     result: any = {},
//     success: boolean = true,
// ) =>
//     cy
//         .intercept("/api/action/" + action, (req) =>
//             req.reply(
//                 Object.assign(
//                     { success },
//                     success ? { result } : { error: result },
//                 ),
//             ),
//         )
//         .as(alias);

// Switch to page that does not contain any interferring JS
before(() => {
    // if you want to test behavior of the authenticated user, call
    // `cy.login()`
    cy.visit("/about");
});

// `describe` is used to group tests by feature
describe("Global code", () => {
    // Every `it` is a test. Do something inside `it` and make assertions in
    // the end.
    it("creates sandbox.bulk.nestedOptions", () => {
        sandbox()
            // select nested property from sandbox
            .its("bulk.nestedOptions")
            .then((func) => {
                // verify output of the `nestedOptions`
                expect(func({})).to.eql({});
                expect(func({ a: 1 })).to.eql({ a: 1 });
                expect(func({ a_b: 10 })).to.eql({ a: { b: 10 } });
                expect(
                    func({ x: 1, a_b: 2, f_g_e: 3, a_c: 4, f_g_l: 5, f_k: 8 }),
                ).to.eql({
                    x: 1,
                    a: { b: 2, c: 4 },
                    f: { g: { e: 3, l: 5 }, k: 8 },
                });
            });
    });
});
