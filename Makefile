## Example:
# make prepare; make full-upgrade
#
## or
# make prepare; make sync install
#
## `make prepare` installs/updates code for all other make-rules. It's
## recommended to execute it periodicatlly, to pull the lates version of CDM.
#
## `make full-upgrade` synchronizes and installs CKAN, dependencies and current
## extension.
#
## `make sync install` synchronizes and installs only dependencies. CKAN and
## current extension are ignored.
#
## Add `develop=1` to install dev-requirements.txt alongside with the normal
## requirements.
#
## Any extension can be synchronized/installed individually:
# make sync-EXT install-EXT
#
## If `remote-EXT` definition is present, extension is pulled from the
## specified source. If you are running `make sync-EXT install-EXT` and there
## is no `remote-EXT` line, CDM makes an attempt to pull the extension from
## master branch of `https://github.com/ckan/ckanext-EXT`. Most likely, such
## extension does not exist. But git will think that you are pulling from
## private repository and may ask your credentials or just say that you don't
## have permissions to read from this repo.

###############################################################################
#                             requirements: start                             #
###############################################################################
# CKAN core supports this short syntax. But internally it's unfolds into
## remote-ckan = https://github.com/ckan/ckan tag ckan-2.10.4
# if you want to use CKAN fork or specific commit, use this full specification
ckan_tag = ckan-2.10.4

# items from this list are installed by `make full-upgrade` and `make sync
# install`. If you specify remote, but did not added extension to this list, it
# won't be installed. If you add SOMETHING to this list, but did not specify
# remote, SOMETHING is pulled from `https://github.com/ckan/ckanext-SOMETHING
# branch master`
ext_list = \
	admin-panel \
	collection cloudstorage comments \
    dcat \
	editable-config \
	files flakes \
	geoview googleanalytics \
    hierarchy harvest \
	let-me-in \
	officedocs or-facet \
	pdfview pygments \
	resource-indexer \
	scheming search-tweaks spatial saml syndicate \
	toolbelt \
	unfold \
	vip-portal \
	xloader

# information about extension source. Format is `ALTERNATIVE-NAME = URL TYPE
# REF`, where
#
# * ALTERNATIVE: `remote` by default, but can be any string
#
# * NAME: name of extension. Must be exactly the same as value from `ext_list`
#
# * URL: repo URL. GitHub, BitBucket, GitLab or even SSH URL
#
# * TYPE: type of reference specified by the next part. One of: branch, commit, tag
#
# * REF: commit hash, branch name, tag name, depending on TYPE value. Prefer tags
remote-admin-panel = https://github.com/mutantsan/ckanext-admin-panel commit 999183a
# dev is an alternative. You can install it via `make full-upgrade
# alternative=dev`. Any other prefix can be used instead of `dev`.
dev-admin-panel = https://github.com/mutantsan/ckanext-admin-panel branch master

remote-cloudstorage = https://github.com/DataShades/ckanext-cloudstorage.git tag v0.3.2
remote-collection = https://github.com/DataShades/ckanext-collection.git tag v0.2.0a0
remote-comments = https://github.com/DataShades/ckanext-comments.git tag v0.3.2a0
remote-dcat = https://github.com/ckan/ckanext-dcat.git tag v1.7.0
remote-editable-config = https://github.com/ckan/ckanext-editable-config tag v0.0.6
remote-files = https://github.com/DataShades/ckanext-files.git tag v1.0.0a0
remote-flakes = https://github.com/DataShades/ckanext-flakes.git tag v0.4.5
remote-geoview = https://github.com/ckan/ckanext-geoview.git tag v0.1.0
remote-googleanalytics = https://github.com/ckan/ckanext-googleanalytics.git tag v2.4.0
remote-harvest = https://github.com/ckan/ckanext-harvest.git tag v1.5.6
remote-hierarchy = https://github.com/ckan/ckanext-hierarchy.git tag v1.2.1
remote-let-me-in = https://github.com/mutantsan/ckanext-let-me-in tag v1.0.1
remote-officedocs = https://github.com/jqnatividad/ckanext-officedocs tag v1.1.0
remote-or-facet = https://github.com/DataShades/ckanext-or_facet tag v0.1.1
remote-pdfview = https://github.com/ckan/ckanext-pdfview.git tag 0.0.8
remote-pygments = https://github.com/mutantsan/ckanext-pygments commit f4287bb
remote-resource-indexer = https://github.com/DataShades/ckanext-resource_indexer.git tag v0.4.1
remote-saml = https://github.com/DataShades/ckanext-saml.git tag v0.3.3
remote-scheming = https://github.com/ckan/ckanext-scheming tag release-3.0.0
remote-search-tweaks = https://github.com/dataShades/ckanext-search-tweaks tag v0.6.1
remote-spatial = https://github.com/ckan/ckanext-spatial tag v2.1.1
remote-syndicate = https://github.com/DataShades/ckanext-syndicate tag v2.2.2
remote-toolbelt = https://github.com/DataShades/ckanext-toolbelt.git tag v0.4.24
remote-unfold = https://github.com/mutantsan/ckanext-unfold.git tag v1.0.2
remote-vip-portal = https://github.com/DataShades/ckanext-vip-portal.git tag v0.2.5a1
remote-xloader = https://github.com/ckan/ckanext-xloader.git tag 1.0.1

# extras installed with the extension. Produce `pip install
# 'ckanext-googleanalytics[requirements]'`-like instructions.
package_extras-remote-googleanalytics = requirements
package_extras-remote-files = opendal,libcloud
package_extras-remote-resource-indexer = pdf



###############################################################################
#                              requirements: end                              #
###############################################################################

# version of CDM pulled during `make-prepare`. Use version tag to prevent
# undesirable udates
_version = master

# import all rules defined in `deps.mk`. This file will be pulled by `make prepare`
-include deps.mk

prepare:  ## download CDM rules
	curl -O https://raw.githubusercontent.com/DataShades/ckan-deps-installer/$(_version)/deps.mk

vendor-dir = ckanext/bulk/assets/vendor

vendor:  ## Copy vendor libraries from node_modules/ to assets directory
	cp node_modules/tom-select/dist/js/tom-select.{base,complete}.min.js $(vendor-dir)
	cp node_modules/tom-select/dist/css/tom-select{,.bootstrap5}.css $(vendor-dir)
	cp node_modules/sweetalert2/dist/sweetalert2.all.min.js $(vendor-dir)/sweetalert2.all.js
	cp node_modules/sortablejs/Sortable.min.js $(vendor-dir)/Sortable.js
	cp node_modules/htmx.org/dist/htmx.min.js $(vendor-dir)/htmx.js
	cp node_modules/hyperscript.org/dist/_hyperscript.min.js $(vendor-dir)/hyperscript.js
	cp node_modules/izimodal/css/iziModal.css $(vendor-dir)
	cp node_modules/izimodal/js/iziModal.js $(vendor-dir)
	cp node_modules/izitoast/dist/css/iziToast.css $(vendor-dir)
	cp node_modules/izitoast/dist/js/iziToast.js $(vendor-dir)
	cp node_modules/slick-carousel/slick/slick.{js,css} $(vendor-dir)
	cp node_modules/slick-carousel/slick/slick-theme.css $(vendor-dir)
	cp node_modules/slick-carousel/slick/ajax-loader.gif ckanext/bulk/public
	cp node_modules/slick-carousel/slick/fonts ckanext/bulk/public/slick-fonts -r
	cp node_modules/daterangepicker/daterangepicker.{js,css} ckanext/bulk/assets/vendor
	cp node_modules/daterangepicker/moment.min.js ckanext/bulk/assets/vendor
	cp node_modules/overlayscrollbars/styles/overlayscrollbars.css ckanext/bulk/assets/vendor
	cp node_modules/overlayscrollbars/browser/overlayscrollbars.browser.es6.js ckanext/bulk/assets/vendor/overlayscrollbars.js

typecheck:  ## Run typechecker
	npx pyright --pythonpath="$$(which python)"


changelog:  ## compile changelog
	git changelog -c conventional -o CHANGELOG.md $(if $(bump),-B $(bump))

test-server:  ## start server for frontend testing
ifeq ($(dirty-server),)
	yes | ckan -c test.ini db clean
	ckan -c test.ini db upgrade
	yes | ckan -ctest.ini sysadmin add admin password=password123 email=admin@test.net
else
	ckan -c test.ini run -t
endif
