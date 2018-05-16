// const HtmlWebPackPlugin = require("html-webpack-plugin");
const webpack = require('webpack');
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
            // 'evennia': './evennia.js',
            'app': './app.js'
        },
    
        output: {
            path: path.resolve(__dirname, '../static/' + portal + '/js/'),
            filename: '[name].min.js', //TODO only on build
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
            // runtimeChunk: {
            //     name: 'vendor'
            // },
            // splitChunks: {
            //     cacheGroups: {
            //         vendor: {
            //             test: path.resolve(__dirname, "node_modules"),
            //             chunks: "initial",
            //             name: "vendor",
            //             minChunks: 1,
            //             priority: 10,
            //             enforce: true
            //         }
            //     }
            // }
        },
    
        stats: {
            modules: false,
            entrypoints: false,
            chunks: false
        },

        plugins: [
			new webpack.NoEmitOnErrorsPlugin()
        ]
    }

    return wp;
};