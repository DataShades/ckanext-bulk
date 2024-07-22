[![Tests](https://github.com/Link Digital/ckanext-bulk/workflows/tests.yml/badge.svg)](https://github.com/Link Digital/ckanext-bulk/actions/workflows/test.yml)

# ckanext-bulk

Extended template of CKAN extension.

## Requirements

Compatibility with core CKAN versions:

| CKAN version | Compatible? |
|--------------|-------------|
| 2.9          | no          |
| 2.10         | yes         |
| 2.11         | yes         |
| master       | yes         |

## Create extension

If you see this, most likely extension is already created. But if you want to
create another extension, here's the example:

1. Install `ckanext-toolbelt`
   [v0.4.21](https://pypi.org/project/ckanext-toolbelt/) or newer.
   ```sh
   pip install -U ckanext-toolbelt
   ```

1. Generate an extension in the **current** directory:

    ```sh
    ctb make ckanext extended
    ```
    or specify output location using `-o`/`--output-dir` option:

    ```sh
    ctb make ckanext extended -o /tmp
    ```

    It's also possible to specify the name of extension (via positional
    argument) and use default answers for questions(`-d`/`--use-defaults`
    flag). In this way you don't need to answer any questions.

    ```sh
    ctb make ckanext extended my-ext -d
    ```

1. Switch to extension folder and install it with `dev` extras:
   ```sh
   cd ckanext-my-ext/
   pip install -e '.[dev]'
   ```

1. Initialize git-repository inside the extension:
   ```sh
   git init
   ```

1. Initialize pre-commit hooks:
   ```sh
   pre-commit install
   ```

1. Optional. If you don't have CKAN and want to install it alongside with
   popular extensions, run:
   ```sh
   make prepare
   make full-upgrade develop=1
   ```
   Create config files for 1st and 3rd lavel(details explained in Configuration
   section):
   ```sh
   ckan generate config default.ini
   ckan generate config ckan.ini
   ```
   Link 2nd level of configuration:
   ```sh
   ln -snf ckanext-my-ext/config/* ./
   ```
   Create solr core using schema from
   `ckanext-my-ext/config/solr/schema.xml`. Create DB.
   Remove content of `[app:main]` from `ckan.ini`. Add `use =
   config:project.ini` line instead and copy/adapt `Environment settings:
   start/end` block from `project.ini`.
   Apply DB migrations:
   ```sh
   ckan db upgrade
   ckan db pending-migrations --apply
   ```


## Usage

This guide explains how you can use the project initialized with the extended
template and add more code to it. If you don't have Markdown viewer and don't
like reading raw markdown source, you can start local server with this guide:

```
# you need to install the extension before running the following command
# $ pip install -e '.[dev]'
mkdocs serve
```

The documentation is available at [localhost:8000](http://localhost:8000/) as
long as server is running.

Additional details can be found in the source code. For example,
`logic/action.py` contains examples and explanations of API actions that can be
registered by extension.


## Code

Code of the extension resides inside `ckanext/bulk`.

### `plugin.py`

The main entry point is `plugin.py`. It extends CKAN using interfaces and every
other file is somehow connected to `plugin.py`.

If possible, avoid writing code directly inside `plugin.py`. Only small and
clear functions should be added to it. And anything that does not fit in dozen
lines can be moved into a separate file.

Default implementation of `plugin.py` extends CKAN using 3 different
approaches.

---

For simple interface, such as `IConfigurer`, it implements the interface
directly and defines `update_config` method. This method registers assets and
templates of the extension. Nothing complex is computed here, and there are no
functions that are hard to read.

This approach is recommended for the following interfaces: `IConfigurer`,
`IConfigurable`, `IMiddleware`, `IFacets`.

---

To hook into one-mehtod interfaces that register additional functions, the
plugin uses
[blankets](https://docs.ckan.org/en/2.10/extensions/plugins-toolkit.html#ckan.plugins.toolkit.ckan.plugins.toolkit.blanket). When
extension is decorated with blanket, it automatically implements corresponding
interface and registers all public members of corresponding module.

There are 7 blankets in CKAN:

| Blanket             | Effect                                                                                              |
|---------------------|-----------------------------------------------------------------------------------------------------|
| actions             | Register all public functions from `ckanext.bulk.logic.action` as actions        |
| auth_functions      | Register all public functions from `ckanext.bulk.logic.auth` as auth functions   |
| blueprints          | Register all blueprints from `ckanext.bulk.views` as blueprints                  |
| cli                 | Register all public members(`__all__`) from `ckanext.bulk.cli` as commands       |
| config_declarations | Register all declarations from `ckanext/bulk/config_declaration.yaml`            |
| helpers             | Register all public functions from `ckanext.bulk.helpers` as helpers             |
| validators          | Register all public functions from `ckanext.bulk.logic.validators` as validators |

Because of blankets, you don't need to import views, CLI commands or actions
into plugin. You don't even have to register `get_actions`-like function. Any
function defined inside `ckanext.bulk.logic.action` will be
registered as an action with the same name, if it's not prefixed with
underscore. Imported functions are not registered as actions: you have to
create function inside the `action` module to export it automatically.

If you keep actions or other code units inside multiple files, you can create
`get_actions`-like function, that returns all actions and pass it to the
blanket:

```python
@tk.blanket.actions(get_actions)
class BulkPlugin(p.SingletonPlugin):
    ...
```

Note: `blueprints` blanket registers only subclasses of `flask.Blueprint`.

Note: `cli` blanket is not very smart and will try to register every command
directly under `ckan` CLI. If you are using `click.group` decorator, it's
recommended to define `__all__` list inside `cli` module and specify names of
commands/groups that must be registered by `IClick` interface.

---


Other interfaces usually are quite complex. The recommended way of implementing
these interfaces(and custom interfaces from extensions, like IFiles) includes
extra steps.

First, create a module inside `ckanext.bulk.implementations`
using snake-case version of the interface name. For example,
`IPackageController` turns into `package_controller.py`, `IAdminPanel` turns
into `admin_panel.py`.

Inside this new module, define a plugin that matches the name of the interface
without `I` prefix. Put implementation of the interface inside this plugin.

```python

class PackageController(SingletonPlugin):
    implements(IPackageController, inherit=True)

    def after_dataset_show(self, context, pkg_dict):
        ...
```

Re-export implementation from `ckanext/bulk/implementations/__init__.py`

```python
from .package_controller import PackageController

__all__ = [
    "PackageController",
]
```

And finally add this implementation as a parent class to your main plugin:

```python
from . import implementations

class BulkPlugin(
    implementations.PackageController,
    p.SingletonPlugin,
):
    ...

```

It's quite a lot of steps, but in this way you can keep your plugin simple and
readable.

### `cli.py`

Define all commands here. It's recommended to create a single `click` group
that maches the name of the plugin and add this group to `__all__` attribute of
the module. As result, only this group will be available as `ckan bulk` CLI command.

All commands should be registered under this group or its subgroups.

Members included into `__all__` attribute are registered as CLI commands by
`cli` blanket.

### `config_declaration.yaml`

YAML file with [config
declarations](https://docs.ckan.org/en/2.10/maintaining/configuration.html#config-declaration).

Declare all custom configuration options here. Never use undeclared config
options in code and provide at least basic declaration. It's also recommended
to declare the type and default value for the config option as well.

You can always dump all the options of the plugin using CKAN CLI:

```sh
ckan config declaration heh -d
```

`-d`/`--include-docs` flag adds description of the option to the output. Omit
it if you need only names and defaults values of the option.

Declarations from this file are automatically registered in CKAN by
`config_declarations` blanket.

### `config.py`

This module simplifies access to config options defined by the plugin.

Instead of accessing untyped options inside `tk.config`, it's recommended to
define typed accessors inside this module. It improves a number of aspects:

* config options can be accessed by shorter name: `option()` instead of
  `tk.config["ckanext.bulk.option.name"]`.
* accessor has specific type, while `tk.config[KEY]` is always `Any`
* any additional processing of options value can be hidden inside the accessor
* you can safely change the name of the config option

### `helpers.py`

This file contains all template helpers for the plugin.

All public members defined in this module are registered as helpers by
`helpers` blanket.

### `views.py`

Here you should register blueprint for the plugin. If you have multiple
blueprints, transform `views.py` into `views/__init__.py` and add every
blueprint as a separate submodule. You'll need to create `get_blueprints`
function and pass it to the blanket:

```python
@tk.blanket.blueprints(get_blueprints)
class HehPlugin(SingletonPlugin):
    ...
```

All blueprints defined in this module are registered as blueprints by
`blueprints` blanket.

### `public/`

This folder contains files that are directly accessible from browser because of
the following line from `update_config` method of `IConfigurer` implementation:

```python
tk.add_public_directory(config_, "public")
```

### `assets/`

This is the base folder for all site assets (CSS and JS files) and source files
for them. For example, if you are using SASS or TypeScript, these files should
also be stored inside assets folder.

Assets cannot be accessed directly. You have to define [named
asset](https://docs.ckan.org/en/2.10/contributing/frontend/assets.html) inside
`assets/webassets.yml` and include this named asset into template using `{% asset "bulk/ASSET_NAME" %}` tag.

### `templates/`

This is the base folder for Jinja2 templates. Templates that override existing
pages must replicate structure of CKAN's `templates` folder. If you are going
to create a completely new page, prefer storing templates for it inside
separate subfolder with the name matching the plugin name. For example,
template for the blog page may be stored as `templates/bulk/blog/index.html`.

### `logic/action.py`

Define API actions here. If you are going to create a lot of actions, consider
transforming `action.py` into `action/__init__.py` and group actions by domain
inside separate files under this new subfolder: `action/blog.py`,
`action/user.py`, `action/something.py`.

All public members defined in this module are registered as API actions by
`actions` blanket.

### `logic/auth.py`

This file contains auth functions. **Every** API action registered by your
plugin must have dedicated auth function. You can define additional auth
functions and use them with `tk.check_access`/`h.check_access` in views and
templates.

All public members defined in this module are registered as auth functions by
`auth_functions` blanket.

### `logic/schema.py`

Validation schemas for API actions. If action accepts arguments it's
recommended to define a schema for this action.

Schemas are not registered inside CKAN. They will not conflict with existing
schemas and you don't need to add plugin name as prefix to schemas.

### `logic/validators.py`

Validators used by plugin.

All public members defined in this module are registered as validators by
`validators` blanket.

### `model/`

Folder for all your models. Define every model in a separate file. Don't forget
to generate migrations for the model using `ckan generate migration -p bulk -m "Migration message"` CLI command.

### `schemas/`

Metadata schemas for ckanext-scheming.

## Configuration

Extension contains `config/` folder at root level. All files related to portal
configurations are stored here. Apart from `project.ini` with the project level
configuration, you can also keep `licenses.json`, `resource_formats.json`,
`who.ini`, SAML2 credentials, GoogleCloud credentials, etc. You can even store
metadata schemas here, but historically they are kept together with the code,
so we suggest leaving them inside `ckanext/bulk/schemas`.

### `project.ini`

Project specific configuration. It contains all the settings that are safe to
keep in repository.

Options that should be modified during deployment are kept inside `Environment
settings` block. Any token/password/ID value must be replaced with placeholder:

```ini
## ckaneext-googleanalytics
googleanalytics.id = G-TEST
```

Alternatively, you can specify interpolation string with reference to
environment variable prefixed by `CKAN_`.

```ini
## ckanext-xloader
ckanext.xloader.api_token = %(CKAN_XLOADER_API_TOKEN)s
```

In the example above, value of `CKAN_XLOADER_API_TOKEN` envvar will be used as
XLoader API Token.

All options that will likely remain unchanged across environments, must be
added after `Environment settings` block.

This configuration file must be used as a middle layer in 3-layers
configuration:

1. Generate `default.ini` using CKAN cli. Do not modify it.
1. Create a symbolic link of `config/project.ini` next to
   `default.ini`. `project.ini` will use defaults from `default.ini`.
1. Generate `ckan.ini` in the same folder where you have `default.ini` and link
   to `project.ini`. Replace the whole content of `[app:main]` section with
   `use = config:project.ini`(to use `project.ini` as source for defaults) and
   copy/adapt `Environment settings` section from `project.ini`.

This approach solves the following problems:

* Expected configuration can be shared across environments because you have
  `project.ini` commited in the repo.
* Configuration changes are applied automatically, because `project.ini` is a
  link to git-controlled file. You don't need to modify CKAN configuration
  manually after the deploy.
* When upgrading to a new CKAN version with new configuration options, or when
  secrets were compromised, you can regenerate `default.ini`. All changes from
  `ckan.ini` and `project.ini` are kept.
* Environment specific configuration is kept inside `ckan.ini`. You clearly
  see, what needs to be configured individually on environment because of
  `Environment settings` block. And you can ignored hundreds of options outside
  this block, because they must be identicall on all environments.

### `solr/`

This folder contains Solr schema. Any modifications must be applied to this
schema and then you can copy the schema into Solr configuration folder after
deployment.

In this way you can use exactly the same schema and control all the
modifications required by different plugin.

It's recommended to leave a comment with mention of plugin that requires the
modification before the modified line.

All additional files required by Solr, like specific version of Solr libraries
can be also added here.

## Included extensions

This exntension includes configuration for a number of popular CKAN
extensions. These extensions are installed when you run `make full-upgrade`.

Usually, you only need to add extension name to `ckan.plugins` config
option. If extension requires additional configuration, it will be mentioned in
the corresponding section below.

### ckanext-admin-panel

Admin UI improvements. Adds panel with links to admin pages at the top of the
page.

Does not require additional configuration. Enabled by default as `admin_panel`
plugin.

### ckanext-cloudstorage

Upload resource files to S3 bucket.

Add `cloudstorage` to the list of enabled plugins.

Add driver configuration
```ini

## ckanext-cloudstorage
ckanext.cloudstorage.container_name = <BUCKET>
ckanext.cloudstorage.driver = S3
ckanext.cloudstorage.driver_options = {"key": "<KEY>", "secret": "<SECRET>",  "host": "s3.ap-southeast-2.amazonaws.com"}
```

### ckanext-collection

Utilities for building reusable interfaces for data series.

Does not require additional configuration. Enabled by default as `collection`
plugin.

### ckanext-comments

Comment threads that can be attached to anything(dataset, group, user,
resource).

Enable `comments` plugin and apply DB migrations `ckan db upgrade -p comments`
to activate comments API. Thread widget must be added manually to pages. For
example, the following block can be used to add thread to `package/read.html`


```jinja
{% block primary_content_inner %}
    {{ super() }}
    {% snippet 'comments/snippets/thread.html', subject_id=pkg.id, subject_type='package' %}
{% endblock primary_content_inner %}
```


### ckanext-dcat

DCAT translator for CKAN.

Does not require additional configuration. Enabled by default as `dcat`
plugin.

### ckanext-editable-config

API for managing CKAN configuration in runtime.

Does not require additional configuration. Enabled by default as `editable_config`
plugin.

### ckanext-files

File management API.

Enabled by default as `files` plugin.

Requires additional configuration:
```ini
## ckanext-files
ckanext.files.storage.default.type = files:fs
ckanext.files.storage.default.path = %(here)s/storage
ckanext.files.storage.default.create_path = true
```

### ckanext-flakes

API for storing arbitrary data in DB.

Add `flakes` to the list of plugins and apply DB migrations: `ckan db upgrade -p flakes`

### ckanext-geoview

Map views for spatial data.

Configure specific view type accoriding to [official
documentation](https://github.com/ckan/ckanext-geoview?tab=readme-ov-file#available-plugins)

### ckanext-googleanalytics

Track user activity using GA.

Add `googleanalytics` plugin and specify `googleanalytics.id` key.

### ckanext-harvest

Transform data from external services into CKAN datasets.

Add `harvest` to the list of plugins.

### ckanext-hierarchy

Group/organization hierarchy.

Enable `hierarchy_display hierarchy_form hierarchy_group_form` plugins. If you
are using scheming, you may also need to update metadata schemas.

### ckanext-let-me-in

One-time login links generator.

Does not require additional configuration. Enabled by default as `let_me_in`
plugin.

### ckanext-officedocs

Views for MS Office documents.

Add `officedocs_view` to the list of plugins and default views.

### ckanext-or-facet

Switch search facets to union logic instead of intersection.

Add `or_facet` to the list of plugins.

### ckanext-pdfview

PDF view for resources.

Enabled by default as `pdf_view`.

### ckanext-pygments

Text views with syntax highlighter.

Add `pygments_view` to the list of plugins and default views.

### ckanext-resource-indexer

Add content of resources to search index.

Add `resource_indexer plain_resource_indexer` to the list of plugins.

### ckanext-saml

SAML2 authentication.

Add `saml` to the list of plugins. Apply DB migrations: `ckan db upgrade -p
saml`. Adapt `ckanext.saml.*` options. If it's not enough, modify
`config/saml/settings.json`.

When everything is configured, pull metadata from IdP: `ckanapi action saml_idp_refresh`.

### ckanext-scheming

JSON/YAML definitions of metadata schemas.

Add `scheming_datasets scheming_groups scheming_organizations` to the list of
plugins.

### ckanext-syndicate

Push local datasets to extenal CKAN portal

Add `syndicate` to the list of plugins. Configure details of remote
portal(syndication profile) specified by `ckanext.syndicate.profile*` options.

### ckanext-search-tweaks

Additional features for CKAN search.

Enable [plugins defined by the
extension](https://github.com/DataShades/ckanext-search-tweaks?tab=readme-ov-file#usage)
and add corresponding configuration

### ckanext-spatial

Features related to spatial search.

Add `spatial_metadata spatial_query` to the list of plugins. Initialize PostGIS extension for CKAN DB

If you are using Docker PostGIS image, you need to do something similar to the example below:

```sh
PG_VERSION=16
POSTGIS_VERSION=3.4
DB=ckan_db_name

psql -U postgres -f /usr/share/postgresql/$PG_VERSION/contrib/postgis-$POSTGIS_VERSION/postgis.sql -d $DB -v ON_ERROR_ROLLBACK=1;
psql -U postgres -f /usr/share/postgresql/$PG_VERSION/contrib/postgis-$POSTGIS_VERSION/spatial_ref_sys.sql -d $DB -v ON_ERROR_ROLLBACK=1
```

Use `config/solr/schema.xml` for solr. If you are going to use `solr-bbox`
search backend, remove the definition of field after `solr-spatial-field`
comment. If you are going to use `solr-spatial-field` backend, use schema as
is. You'll also need to [add JTS
library](https://solr.apache.org/guide/8_11/spatial-search.html#jts-and-polygons-flat)
to `server/solr-webapp/webapp/WEB-INF/lib/` folder of your Solr service.

[Extra details about search
backend](https://docs.ckan.org/projects/ckanext-spatial/en/latest/spatial-search.html#choosing-a-backend-for-the-spatial-search).


### ckanext-toolbelt

Different helpers that are often used but are too small for individual
extensions.

Functionality of toolbelt usually does not require enabling plugins. Just
import and use it.

### ckanext-unfold

Views for archives

Depending on the format of archive, requirements and configuration can be
different. Check [official
documentaion](https://github.com/mutantsan/ckanext-unfold).

### ckanext-vip-portal

Restrict access to specific pages globally(for anonymous user) or individually.

Add `vip_portal` to the list of enabled plugins.

### ckanext-xloader

Load files into DataStore tables.

Add `xloader` to the list of plugins. Configure `ckanext.xloader.api_token`
option.


## Additional tools

This extension contains a set of tools for code quality control, executing
tasks, building assets. Some of them, like tests and benchmarks, will be
written by you. There are some examples available inside files for such
tools. Other, like code-style checker, already configured and you only need to
run specific command.

Here's the overview of all additional tools that are available inside this
extension.

### Git hooks: [pre-commit](https://pre-commit.com/)

This extension contains git hooks that are automatically executed before making
commit. These hooks check *modified* files and prevent commit if you are trying
to include changes that violate project rules.

Because hooks are executed before each commit, only actions that can be
performed instantly are added to hooks.

Hooks described below are executed before every commit. They check modified
files and, if file has problems, reject the commit. You have to fix the issue,
add fixes to index `git add ...` and run commit command once again. Some
problems are fixed automatically, but commit is still rejected. You need to
review auto-fixes, add them to index and repeat the commit.

| Hook                | Effect                                                                  |
|---------------------|-------------------------------------------------------------------------|
| end-of-file-fixer   | Ensure that file contains a single new line in the end                  |
| trailing-whitespace | Ensure that there are no trailing whitespaces on every line of the file |
| ruff                | Check standard code style issues                                        |
| ruff-format         | Format code using black-compatible rules(but faster than black)         |

Note: `ruff` hooks read configuration from `pyproject.toml`.

In addition, as an example, before push repository is checked for presence of
debug statemens(`print`, `breakpoint`). If you left them in code, push is
rejected.

#### Initialization

```sh
pip install -U pre-commit
pre-commit install
```

Note: `pre-commit` dependency is added to `dev` extras of the package and
automatically installed when you run `pip install -e '.[dev]'`. Usually you
only need to run `pre-commit install`.

This command needs to be executed when you created the extension and
initialized the repo. In addition, this command must be executed when you clone
the extension, because hooks are not automatically installed inside clonned
repo.

Once you executed `pre-commit install` inside the repo, hooks will be
automatically applied. If you change configuration of hooks, changes are
applied automatically as well. There is no need to install hooks multiple
times.

Hooks can be removed by running `pre-commit uninstall` or disabled for a single
commit via `-n` flag: `git commit -n ...`.

#### Add new hooks

Choose hook from [this list](https://pre-commit.com/hooks.html). Open
documentation of the corresponding repo and search an example of hook
configuration.

Sometimes, there will be no example, like in case of [Markdown
lint](https://github.com/markdownlint/markdownlint). In this case, you can
manually write configuration of the hook. First, add a new item to `repos` list
inside `.pre-commit-config.yaml`. Add repository url to `repo` attribute of
this new item.

```yaml
- repo: https://github.com/markdownlint/markdownlint
```

Now, choose the latest tag of the repository and set it as value of `rev`:

```yaml
- repo: https://github.com/markdownlint/markdownlint
  rev: v0.13.0
```

Finally, open `.pre-commit-hooks.yaml` file of the [repository with
hooks](https://github.com/markdownlint/markdownlint/blob/main/.pre-commit-hooks.yaml). It
contains definitions of all hooks provided by the repo. Choose hook and add it
as `{"id": HOOK_ID}` inside `hooks` attribute of the configuration.

```yaml
- repo: https://github.com/markdownlint/markdownlint
  rev: v0.13.0
  hooks:
    - id: markdownlint
```

#### Security

`pre-commit` configuration contains configuration for
[gitleaks](https://github.com/gitleaks/gitleaks) and
[talisman](https://github.com/thoughtworks/talisman).

These hooks can be pretty slow so they are disabled by default. But it's
recommended to enable at least one of them to prevent accidental commits with
credentials.


### Asset builder: [gulp](https://gulpjs.com/)

For compiling SCSS into CSS and similar tasks, extension uses
`gulpfile.js`. It's a relatively simple task runner for NodeJS.

Note: usually, any NodeJS version after v12 can be used with the gulpfile. But
it's recommended to use NodeJS specified in `.node-version`/`.nvmrc`. If you
are using `fnm`/`n`/`nvm`/any other NodeJS version manager, it should
automatically read this file and use expected version of NodeJS.

#### Initialization

```sh
npm ci
```

#### Execute task

All available gulp tasks can be checked using `npx gulp --tasks`. Any of the
listed tasks can be executed as `npx gulp <TASK>`, for example: `npx gulp
build`.

For simplicity, two tasks are exposed via `npm` scripts:

* `watch`: wait for changes, recompile styles and include sourcemaps. `npm run
  dev`
* `build`: recompile and minify styles. `npm run build`

#### Add task

Create a function inside `gulpfile.js`. The simplest function starts from call
to `src`, that selects a file. Then you need to chain `.pipe` calls to specify
transformations applied to file. Finally, the last `.pipe` call should contain
result of `dest` call, which specifies the destination directory of the
file. The name of the file is not changed(but you can apply `.pipe` that
renames the file).

For example, here's the function that copies `gulpfile.js` into `ooops`:

```js
const cp = () => src('gulpfile.js').pipe(dest("ooops"))
```

When function is created, you need to register it as task. Assign the function
to any attribute of `exports` object. The name of the attribute is the name of
the task. For example, if you want to expose `cp` function defined above as
`COPY` task:

```js
exports.COPY = cp;
```

Now you can call the task via `npx gulp COPY` and you'll see
`ooops/gulpfile.js` when command completed.

### CKAN dependency management: [CDM](https://github.com/dataShades/ckan-deps-installer)

CDM is a set of Make-rules that install CKAN extensions. Normal python
dependencies(not a CKAN extension) must be added to `install_requires` section
inside `setup.cfg` instead of using CDM.

Things that CDM does can be done via pip and requirements.txt. Generally, we
are using CDM to hide complex commands from the person who installs or deploys
the project.

You should always run `make prepare` before using CDM. This command initializes
and updates CDM. If you see something like `make: *** No rule to make target
'install'.  Stop.`, most likely you forget to execute `make prepare`.

The recommended way of using CDM is running `make full-upgrade`. This command
downloads CKAN source, all required extensions, switches everything to expected
branch/tag/commit and install everything.

If you are going to modify extension, you probably want to install
dev-dependencies from `dev-requirements.txt` of CKAN and extensions. Add
`develop=1` to achieve this:

```sh
make full-upgrade develop=1
```

This command takes a lot of time, as it reinstalls every extension and CKAN
itself. You can make the process faster, if you want to update only specific
part of the codebase.

If you want to synchronize(switch to expected branch/tag/commit) and install
only CKAN, run

```sh
make ckan-sync ckan-install
```

If you want to synchronize and install all extensions(but not the CKAN), run

```sh
make sync install
```

If you want to synchronize and install just a single extension, find it's name
inside `ext_list` variable of `Makefile`(you need to use the exact value,
including letter case, hyphens and underscores). Then run the next command
replacing `NAME` with the name of extension:

```sh
make sync-NAME install-NAME
```


#### Initialization

```sh
make prepare
```

#### Upgrading CKAN

Modify `ckan_tag` inside `Makefile`, using new version tag and run `make
full-upgrade`.

#### Add dependency

Modify `Makefile`:

* add `remote-NAME` record replacing `NAME` with the name of new
  dependency. Record is composed of the repo URL, reference type(`tag`,
  `commit`, `branch`), and value of the reference.
* add `NAME` to `ext_list`. `NAME` added to `ext_list` must be exactly the same
  as name used in `remote-NAME`.
* If you need extras(`pip install ckanext-something[extra1,extra2]`), specify
  them as `package_extras-remote-NAME = extra1,extra2` after all `remote-`
  lines.

Run `make full-upgrade`.

#### Use different version of the dependency on certain environments

If you are using branch `master` on PROD, but want to test branch `develop` on
DEV or locally, you can add *alternative* remotes.

Let's assume you already have `remote-NAME = https://github/url branch master`
inside Makefile. This is the default version of dependency, that is used by
`full-upgrade` and `sync` make-rules.

Now, add `dev-NAME = https://github/url branch develop` to Makefile. The main
point here, you need to replace `remote-` prefix, with `dev-` prefix. You can
also change URL of the repo, type of the reference or reference value(in the
example branch `master` changed to `develop`).

From this moment you can add `alternative=dev` to any command:

```sh
make full-upgrade alternative=dev
make sync install alternative=dev
make sync-NAME install-NAME alternative=dev
```

When `alternative=...` is added, makefile tries to install dependency using
`<alternative name>-` prefix(`dev-` in our case) instead of `remote-`. If
dependency with such prefix is found, it will be installed. If there is no such
dependency, default version with `remote-` prefix is used. That's why all
dependencies that do not have `dev-` version are still available.

You can add as many alternatives as you want:
```sh
dev-NAME = https://github/url branch develop
uat-NAME = https://github/url branch develop
local1-NAME = https://github/url branch develop
local2-NAME = https://github/url branch develop
super-local-NAME = https://github/url branch develop
```

Every alternative is used only when you run make-rule with corresponding value
of `alternative=...` argument.

### Typechecker: [pyright](https://microsoft.github.io/pyright/)

Extension uses `pyright` to verify correctness of types. To run the checker,
use `npx pyright` or `make typecheck` command

Typechecker is not included into git hooks because it is not fast enough. But
you should always check types before the commit: any type error is as bad for
the project as any other code-style issue, or even more serious. Developer may
rely on typing system to simplify and optimize the code, so using uncertain or
invalid types is a bad habit.

There are 3 recommendations regarding typing:

* every function must use typed parameters and typed output if it's different
  from `None`.
* generics/containers must include specification for the items. I.e, `list`
  and `dict` are not allowed, use `list[Any]` and `dict[str, Any]` instead.
* `Any` is allowed, but not recommended. Prefer using specific type, union or
  generic.


```python

## GOOD
def sum(a: int, b: int) -> int:
    return a + b

## BAD: result should be specified, even if it's inferred
def sum(a: int, b: int):
    return a + b

## GOOD: result is `None`, so you can omit specification of return value
def remove(path: str):
    os.path.unlink(path)

## BAD: incomplete generic type should be avoided.
## It's better to use `list[Any]` instead of `list`.
def sort(items: list):
    items.sort()

## BAD: use union `list[Any] | dict[str, Any]`
def sort(items: Any):
    if isinstance(items, list):
        items.sort()
    elif isinstance(items, dict)
        ...
    else:
        raise TypeError
```

#### Initialization

```sh
npm ci
```

#### Configuration

Pyright configuration is managed by `[tool.pyright]` section of
`pyproject.toml`.

### Code-style checker and formatter: [ruff](https://docs.astral.sh/ruff/)

Extension uses `ruff` as linter and auto-formatter. Ruff contains
implementation of various code-checkers and can also do the same things as
`black` or `isort`.

#### Check the code

```sh
ruff check .
```

#### Fix problems(not every problem can be fixed automatically)

```sh
ruff check --fix .
```

#### Format the code

```sh
ruff format .
```

#### Configuration

Ruff configuration is managed by `[tool.ruff.*]` sections of `pyproject.toml`.


### Unit tests: [pytest](https://docs.pytest.org/)

Majority of tests for the extension is written using `pytest`.

`ckanext/bulk/tests` contains examples of tests for standard
operations. Every `test_*.py` file contains tests. Every `conftest.py` file
defines fixtures that are available for modules on the same level and child
modules.

`ckanext/bulk/tests/benchmarks` contains benchmarks. They
are written in the same way as normal tests, but we are using them to measure
code performance. By default, all benchmarks are excluded from selection when
pytest in running. You need to run benchmarks explicitely using `-m benchmark`
argument of `pytest` command.

```sh
pytest -m benchmark
```

The bigger project grows, the more risks appear when you update something or
add a new functionality. Even though tests do not guarantee that nothing is
broken, they can help a lot. When you forget about certain feature, if it's
covered by test, you'll likely notice when it stop working. And upgrading CKAN
core becomes much more predictable when you have tests for main parts of you
project.

If possible, try achieving 100% test coverage. To measure current coverage, use

```sh
## print coverage to terminal
pytest --cov=ckanext.bulk

## generate HTML report at htmlcov/index.html
pytest --cov=ckanext.bulk --cov-report html
```

#### Run tests

Run all tests

```sh
pytest
```

Run tests from `ckanext/bulk/tests/test_plugin.py`

```sh
pytest ckanext/bulk/tests/test_plugin.py
```

Run only tests that failed during previous test session

```sh
pytest --lf
```

Stop execution after first failed test

```sh
pytest -x
```

Run only tests that contain `hello` and `world` in their full path. Full path
contains filepath, class and test name: `ckanext/bulk/tests/test_smth.py:TestSmth:test_smth`

```sh
pytest -k "hello and world"
```

#### Produce coverage report

```sh
pytest --cov=ckanext.bulk
```

#### Run benchmarks

```sh
pytest -m benchmark
```

#### Configuration

Pytest configuration is managed by `[tool.pytest.ini_options]` section of
`pyproject.toml`.

### End-to-end tests: [cypress](https://www.cypress.io/)

You can test functions, action, views using pytest. But testing JS modules
requires a different approach. And you may find writing e2e tests simpler with
cypress, that pytest, because you can visualize the process.

Cypress is used by this extension to perform testing in browser. Cypress opens
application in a real browser and visits different pages, so you need a running
CKAN application to run cyppress tests.

You can use any application that is served on localhost:5000 and has `admin`
user with password `password123`. There is a make-rule that starts such server
using `test.ini` and creates required user. As it uses `test.ini`, you have to
configure test environment before using it.

```sh
make test-server
```

With test server started in a separate terminal, you can run e2e tests in
headless mode(without opening the browser):

```sh
npx cypress run
```

But if you are not familiar with cypress, you may find running tests inside
interactive session more convenient:

```sh
npx cypress open
```

#### Write tests

Tests are defined inside `cypress/e2e/` directory. You'll find examples there.

#### Run tests

```sh
npx cypress run
```

#### Initialization

```sh
npm ci
make test-server
```
