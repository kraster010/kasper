// const HtmlWebPackPlugin = require("html-webpack-plugin");
const path = require('path');

module.exports = function(portal = "webclient", config) {

    var wp = {

        mode: 'development',
        // --watch true, --watch false
        watch: false,
        watchOptions: {
			poll: 1000,
			aggregateTimeout: 500,
		},
        // set basedir for entry point
        context: path.resolve(__dirname, './' + portal + '/src/assets/js/' ),
    
        externals: {
            jquery: "jQuery",
            $ : "jQuery",
        },
    
        entry: {
            'evennia': './evennia.js',
            'main': './index.js'
        },
    
        output: {
            path: path.resolve(__dirname, '../build/' + portal + '/js/'),
            filename: '[name].min.js', //TODO only on build
            // filename: '[name]-[hash].min.js',
            libraryTarget: 'umd',
            library: ['TG', '[name]'],
            umdNamedDefine: true
        },

        resolve: {
			modules: [
				'node_modules',
				'./'
				]
		},

        module: {
            rules: [{
                test: /\.(js)$/,
                loader: 'babel-loader',
                query: {
                    babelrc: false,
                    presets: [
                        ["env", {
                            modules: false
                        }]
                    ],
                }
            }, 
        ]},
    
        // plugins: [
            // new HtmlWebPackPlugin({
            //     inject: "head",
            //     minify: false,
            //     template: "index.html",
            //     filename: "../index.html"
            // }),
        // ],
    
        optimization: {
            runtimeChunk: {
                name: 'vendor'
            },
            splitChunks: {
                cacheGroups: {
                    vendor: {
                        test: path.resolve(__dirname, "node_modules"),
                        chunks: "initial",
                        name: "vendor",
                        minChunks: 1,
                        priority: 10,
                        enforce: true
                    }
                }
            }
        },
    
        stats: {
            modules: false,
            entrypoints: false,
            chunks: false
        }
    }

    return wp;
};