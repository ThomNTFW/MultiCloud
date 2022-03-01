let NAMES = {
    '1': {
        name: 'Shoes',
        sources: { 1: 'Brands Gateway', 2: 'Gilli', 3: 'Judson', 4: 'Alanic' },
        targets: { 1: 'New York', 2: 'Seattle', 3: 'Miami', 4: 'Boston', 5: 'Austin' }
    },
    '2': {
        name: 'Jeans',
        sources: { 1: 'Vervet', 2: 'Tyche', 3: 'Giti', 4: 'Lush' },
        targets: { 1: 'Dallas', 2: 'San Jose', 3: 'Detroit', 4: 'Cleveland', 5: 'Portland' }
    },
    '3': {
        name: 'Hats',
        sources: { 1: 'Esley', 2: 'Kori', 3: 'Mystree', 4: 'Wislande' },
        targets: { 1: 'Chicago', 2: 'Washington', 3: 'Nashville', 4: 'Kansas', 5: 'Atlanta' }
    }
}

function fetch (url, options = {}) {
    // Common metadata
    options.headers = options.headers || {};
    options.headers['X-Requested-With'] = 'XMLHttpRequest'; // Allows server to check for CSRF.
    options.credentials = 'same-origin'; // append cookies

    // Transform body into something consumable by server.
    if (options.body) {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(options.body);
    }
    return window.fetch(url, options).then(res => {
        let contentType = res.headers.get('Content-Type');
        if (contentType && contentType.indexOf('application/json') > -1) {
            return res.json();
        } else {
            return res.text().then(msg => {
                if (res.status >= 400) {
                    throw new Error(msg);
                } else {
                    return res;
                }
            });
        }
    });
}

export default class DataService {
    static getStockDetails () {
        return fetch('/api/available_stock').then(res => {
            return {
                stock: res.stock.map(s => ({
                    id: s.id,
                    sku: NAMES[s.sku].name,
                    source: NAMES[s.sku].sources[s.source],
                    capacity: s.capacity
                })),
                demand: res.demand.map(d => ({
                    id: d.id,
                    sku: NAMES[d.sku].name,
                    target: NAMES[d.sku].targets[d.target],
                    demand: d.demand
                })),
                links: res.links.map(l => ({
                    sku: NAMES[l.sku].name,
                    source: NAMES[l.sku].sources[l.source],
                    target: NAMES[l.sku].targets[l.target],
                    margin: ((l.price_sale - (l.cost_upstream + l.cost_source + l.cost_link + l.cost_target)) / l.price_sale * 100).toFixed(2) + '%'
                }))
            }
        });
    }

    static getOptimization (sku_source_ids, margin) {
        return fetch('/api/trigger_optimization', {
            method: 'POST',
            body: { sku_source_ids, margin }
        }).then(res => {
            if (res.message) {
                return res;
            }

            return {
                dynamic_allocation: res.dynamic_allocation.map(r => ({
                    sku: NAMES[r.sku].name,
                    source: NAMES[r.sku].sources[r.source],
                    target: NAMES[r.sku].targets[r.target],
                    transfer: r.transfer
                }))
            };
        });
    }
}
