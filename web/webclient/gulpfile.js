// load plugins
const gulp = require('gulp'),
	_ = require('lodash'),
	argv = require('minimist')(process.argv),
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
	webpackStream = require('webpack-stream');


const log = console.log;

// // webpack configuration file
const webpack_config = require("./webpack.config.js");
const postcss_config = require("./postcss.config.js")

var paths = {
	src : {
		scss : "./src/scss/**/*.scss",
		js: "./src/js/**/*.js"
	},
	static : {
		js: "",
		scss: ""
	}
}


// compile javascript with webpack
function jsCompile(watch) {

	webpack_config.watch = watch;
	// webpackstream override src and gulp dest
	return gulp.src(paths.src.js, {
			base: './'
		})
		.pipe(cache('js'))
		.pipe(plumber())
		.pipe(webpackStream(webpack_config, webpack))
		.pipe(gulp.dest('static_overrides/webclient/js/'))
		.pipe(debug());

}

// watch sass files for changes then compile and upload
gulp.task( 'sass-watch', () => {
	var watcher = gulp.watch(paths.src.scss, { interval: 500, usePolling: true}, gulp.series('sass-compile'))
		watcher.on('all', (event, path) => {
			console.log('File ' + path + ' was ' + event + ', running tasks...' );
	});
});

// compile sass files
gulp.task('sass-compile', () => {

	return gulp.src(paths.src.scss)
		// .pipe( sourcemaps.init() : gutil.noop() )
		.pipe(sass({
			errLogToConsole: true
		}).on('error', sass.logError))
		.pipe(sassUnicode())
		.pipe(postcss(postcss_config))
		// .pipe( config.options.scss_sourcemaps ? sourcemaps.write('../maps') : gutil.noop() )
		.pipe(gulp.dest('static_overrides/webclient/css'))
		.pipe(debug());
});

gulp.task('js-watch', jsCompile.bind(this, true));
gulp.task('js-compile', jsCompile.bind(this, false));


gulp.task('clean', () => {
	return del('static/webclient/**/*');
});

gulp.task('dev', gulp.series(gulp.parallel('sass-watch', 'js-watch')));
gulp.task('build', gulp.series('clean', 'js-compile', 'sass-compile'));