let config = {
    contentBase: 'public',
    port: 80,
    hot: true
};

if (process.env.DEV_MODE === 'mock') {
    config.before = app => {
        let mockdata = require('./mock-data');

        app.get('/api/available_stock', (req, res) => {
            res.status(200).send(mockdata.available_stock);
        });

        app.post('/api/trigger_optimization', (req, res) => {
            res.status(200).send(mockdata.trigger_optimization);
        });
    };
} else {
    config.proxy = {
        '/api': 'http://localhost:5000'
    }
}

module.exports = config;