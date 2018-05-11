const HtmlWebPackPlugin = require("html-webpack-plugin");
const path = require('path');

module.exports = {
    mode: 'development',


    watch: false,
    // set basedir for entry point
    context: path.resolve(__dirname, './src/webclient'),

    externals: {

        jquery: "jQuery",
        $ : "jQuery",
        // bootstrap: 'bootstrap',
    },

    entry: {
        'evennia': './js/evennia.js',
        'main': './js/index.js'
    },

    output: {
        path: path.resolve(__dirname, './static_overrides/webclient/js/'),
        filename: '[name].min.js', //TODO only on build
        // filename: '[name]-[hash].min.js',
        libraryTarget: 'umd',
        library: ['TG', '[name]'],
        umdNamedDefine: true
    },

    watchOptions: {
        poll: 1000,
        aggregateTimeout: 500,
    },

    module: {
        rules: [{
            test: /\.html$/,
            use: [{
                loader: "html-loader",
                options: {
                    minimize: false
                }
            }]
        }, {
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

    plugins: [
        // new HtmlWebPackPlugin({
        //     inject: "head",
        //     minify: false,
        //     template: "index.html",
        //     filename: "../index.html"
        // }),
    ],

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
};