/**
 * Configuration for gulp tasks
 */
const { resolve } = require("path");
const { src, dest, watch } = require("gulp");

const if_ = require("gulp-if");
const sourcemaps = require("gulp-sourcemaps");
const sass = require("gulp-sass")(require("sass"));
const postcss = require("gulp-postcss");
const combineQueries = require("postcss-sort-media-queries");
const touch = require("gulp-touch-fd");
const cleanCSS = require("gulp-clean-css");

// helper that used to modify behavior of pipes and produce extra debug details
// when DEBUG envvar is present.
const isDev = () => !!process.env.DEBUG;

// root dir that contains all source assets and gulp output
const assetsDir = resolve(__dirname, "ckanext/bulk/assets");

// path to base directory of SASS theme
const srcDir = resolve(assetsDir, "scss");
// path to output directory of compiled theme
const destDir = resolve(assetsDir, "styles");

/**
 * Compile SASS sources into CSS theme.
 */
const build = () =>
  src(resolve(srcDir, "bulk.scss"))
    // keep details about original SASS code
    .pipe(if_(isDev, sourcemaps.init()))

    // compile SASS into CSS. includePaths directive enables import from
    // node_modules packages
    .pipe(sass({ includePaths: ["node_modules"] }).on("error", sass.logError))

    // group identical @media queries into single block and sort them using
    // mobile-first order
    .pipe(postcss([combineQueries]))

    // add source maps if DEBUG enabled. Minify and optimize CSS otherwise
    .pipe(if_(isDev, sourcemaps.write(), cleanCSS({ level: 2 })))

    // write output to destination folder
    .pipe(dest(destDir))

    // update modification date of CSS to force re-building WebAssets by CKAN
    .pipe(touch());

/**
 * Recompile theme immediately and after any change of SCSS files inside source
 * directory.
 */
const watchStyles = () =>
  watch(resolve(srcDir, "**/*.scss"), { ignoreInitial: false }, build);

exports.watch = watchStyles;
exports.build = build;
