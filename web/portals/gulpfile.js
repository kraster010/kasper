const gulp = require('gulp'),
	_ = require('lodash'),
	cache = require('gulp-cached'),
	debug = require('gulp-debug'),
	del = require('del'),
	exec = require('child_process').exec,
	fs = require('fs'),
	gutil = require('gulp-util'),
	jsbeautify = require('gulp-jsbeautify'),
	plumber = require('gulp-plumber'),
	postcss = require('gulp-postcss'),
	rename = require('gulp-rename'),
	sass = require('gulp-sass'),
	sassbeautify = require('gulp-sassbeautify'),
	sassUnicode = require('gulp-sass-unicode'),
	sourcemaps = require('gulp-sourcemaps'),
	uglify = require('gulp-uglify'),
	webpack = require('webpack'),
	chalk = require('chalk'),
	argv = require('yargs').argv,
	webpackStream = require('webpack-stream');


const log = console.log;

const paths = {
	webclient : {
		src : {
			base: "./webclient/src/assets/", 
			scss : "scss/**/*.scss",
			js: "js/"
		},
		out : {
			base: "./out/webclient/",
			js: "js/",
			css: "css/"
		}
	}
}
	
var portal = "webclient"; //default
	//seting different portal building via --portal arg (website, admin etc)
if (argv.live) {
	paths[portal].out.base = "../static/webclient/";
};

if (argv.portal == 'webclient') {
portal = argv.portal
};

let P = paths[portal]; // just short var

// Configuration files
const webpack_config = require("./webpack.config.js")(portal, paths);
const postcss_config = require("./postcss.config.js")

const devBuild = ((process.env.NODE_ENV || 'development').trim().toLowerCase() === 'development');


// compile javascript with webpack
function jsCompile(watch) {

	webpack_config.watch = watch;
	// webpackstream override src and gulp dest
	return gulp.src(P.src.base + P.src.js + '**/*.js', {
			base: './'
		})
		.pipe(cache('js'))
		.pipe(plumber())
		.pipe(webpackStream(webpack_config, webpack))
		.pipe(gulp.dest(P.out.base + P.out.js))
		.pipe(debug());
}

// Watch sass files for changes then compile and upload
gulp.task( 'sass-watch', () => {
	var watcher = gulp.watch(P.src.base + P.src.scss, { interval: 500, usePolling: true}, gulp.series('sass-compile'));
		watcher.on('all', (event, path) => {
			console.log('File ' + path + ' was ' + event + ', running tasks...' );
	});
});

// Compile sass files
gulp.task('sass-compile', () => {
	return gulp.src(P.src.base + P.src.scss)
		// .pipe( sourcemaps.init())
		.pipe(sass({
			errLogToConsole: true
		}).on('error', sass.logError))
		.pipe(sassUnicode())
		.pipe(postcss(postcss_config))
		// .pipe(paths.src.base + 'css' ? sourcemaps.write('./maps'))
		.pipe(gulp.dest(P.out.base + P.out.css))
		.pipe(debug());
});

gulp.task('js-watch', jsCompile.bind(this, true));
gulp.task('js-compile', jsCompile.bind(this, false));


// Cleaning build folder
gulp.task('clean', () => {
	return del( P.out.base + '**/*');
});

gulp.task('dev', gulp.parallel('sass-watch', 'js-watch'));
gulp.task('build', gulp.series('clean', 'js-compile', 'sass-compile'));

