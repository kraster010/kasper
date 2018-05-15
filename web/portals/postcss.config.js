const autoprefixer = require('autoprefixer');
const cssnano = require('cssnano');
module.exports = function() {
	let plugins;
    return plugins = [
        autoprefixer({browsers: ['last 1 version']}),
        cssnano()
    ];
};
