"""Tests for ckanext.bulk.view.

Here you define functional tests that verify page rendering process. It's also
possible to test views using cypress.

Pytest performs better when you want to something on server side befor the
assertion. Cypress should be preferred when you only test user interaction with
frontend without executing arbitrary python code.
"""

import bs4
import pytest
from faker import Faker

import ckan.plugins.toolkit as tk
from ckan.tests.helpers import CKANTestApp


# blueprints are registered when plugin is enabled, so `with_plugins` is
# mandatory fixture for any view test.
@pytest.mark.usefixtures("with_plugins")
def test_page(app: CKANTestApp):
    """Basic page is rendered without errors."""
    resp = app.get(tk.url_for("bulk.page"))
    assert resp.status_code == 200
    assert resp.body == "Hello, bulk!"


@pytest.mark.usefixtures("with_plugins")
def test_page_redirect(app: CKANTestApp):
    """Basic page is rendered without errors."""
    # application follows redirects automatically. In order to check presence
    # of `Location` header, you need to disable this default behavior.
    resp = app.get(
        tk.url_for("bulk.page_redirect"),
        follow_redirects=False,
    )

    assert resp.status_code == 302

    # `Location` header contains absolute URL to the target page
    expected = tk.url_for("bulk.page", _external=True)
    assert resp.headers["location"] == expected


@pytest.mark.usefixtures("with_plugins")
class TestComplex:
    def test_get(self, app: CKANTestApp, faker: Faker):
        """Complex page is rendered with expected content."""
        word = faker.word()
        resp = app.get(tk.url_for("bulk.complex", word=word))
        # BeautifulSoup parses the response content and produces searchable DOM
        # tree.
        page = bs4.BeautifulSoup(resp.body)

        # select element from the page using CSS selector. Selecting elements
        # by tag name is not wise, but we know that page contains exactly one
        # heading.
        heading = page.select_one("h1")
        assert heading
        assert heading.text == f"Hello, {word}!"

    def test_post_invalid(self, app: CKANTestApp, faker: Faker):
        """Complex page shows an error when arguments are missing."""
        word = faker.word()
        resp = app.post(tk.url_for("bulk.complex", word=word))
        page = bs4.BeautifulSoup(resp.body)

        # `.select` selects all elements matching selector, while `.select_one`
        # returns only the first.
        errors = {x.text.strip() for x in page.select(".flash-messages .alert")}

        # use set to avoid errors because of unknown order of messages
        assert errors == {
            "Left: Missing value",
            "Right: Missing value",
        }

    def test_post_valid(self, app: CKANTestApp, faker: Faker):
        """Complex page shows no errors for valid requests."""
        word = faker.word()
        resp = app.post(
            tk.url_for("bulk.complex", word=word),
            data={"left": "1", "right": "2"},
        )
        page = bs4.BeautifulSoup(resp.body)

        assert page.select(".flash-messages .alert") == []
