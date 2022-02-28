import node_resolve from '@rollup/plugin-node-resolve';
import babel from '@rollup/plugin-babel';
import hotcss from 'rollup-plugin-hot-css';
import static_files from 'rollup-plugin-static-files';
import { terser } from 'rollup-plugin-terser';
import prefresh from '@prefresh/nollup';
import license from 'rollup-plugin-node-license';
import alias from 'rollup-plugin-alias';
import svgr from '@svgr/rollup';
import path from 'path';

let config = {
    input: './src/main.js',
    output: {
        dir: 'dist',
        format: 'esm',
        entryFileNames: '[name].[hash].js',
        assetFileNames: '[name].[hash][extname]'
    },
    plugins: [
        alias({
            entries: ['react', 'react-dom'].map(find => (
                { find, replacement: path.resolve(__dirname, './node_modules/preact/compat/dist/compat.module.js') }
            ))
        }),
        hotcss({
            hot: process.env.NODE_ENV === 'development',
            file: 'styles.css',
            loaders: ['scss']
        }),
        svgr(),
        babel({
            exclude: 'node_modules/**'
        }),
        node_resolve(),
        process.env.NODE_ENV === 'development' && prefresh()
    ]
}

if (process.env.NODE_ENV === 'production') {
    config.plugins = config.plugins.concat([
        static_files({
            include: ['./public']
        }),
        terser(),
        license()
    ]);
}

export default config;
