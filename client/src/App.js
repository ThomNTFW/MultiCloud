import { useState, useEffect } from 'preact/hooks';
import Table from './table/Table';
import DataService from './DataService';
import Loader from './loader/Loader';
import LinksGraph from './links-graph/LinksGraph';
import './App.scss';

const SUPPLIER_COLUMNS = [{
    title: 'Source',
    property: 'source'
}, {
    title: 'Capacity',
    property: 'capacity'
}];

const DEMAND_COLUMNS = [{ 
    title: 'Target',
    property: 'target'
}, {
    title: 'Demand',
    property: 'demand'
}];

export default function App () {
    let [ skus, setSkus ] = useState([]);
    let [ selectedSku, setSelectedSku ] = useState('');
    let [ stock, setStock ] = useState([]);
    let [ demand, setDemand ] = useState([]);
    let [ links, setLinks ] = useState([]);
    let [ selectedStock, setSelectedStock ] = useState([]);
    let [ loading, setLoading ] = useState(false);
    let [ optimized, setOptimized ] = useState(null);
    let [ error, setError ] = useState('');
    let [ linksGraphMode, setLinksGraphMode ] = useState('plan');

    // On load, fetch all of the stock and demand information
    useEffect(() => {
        DataService.getStockDetails().then(res => {
            let skus = [...new Set(res.stock.map(s => s.sku))]
            setSkus(skus);
            setSelectedSku(skus[0]);
            setStock(res.stock);
            setDemand(res.demand);
            setLinks(res.links);
            setSelectedStock(res.stock.map(s => s.id));
        });
    }, []);

    function onStockSelect (e) {
        let index = selectedStock.indexOf(e);
        if (index > -1) {
            setSelectedStock(selectedStock.filter(v => v !== e));
        } else {
            setSelectedStock(selectedStock.concat(e));
        }
    }

    function onSkuSelect (e) {
        let value = e.target.value;
        setSelectedSku(value);
        setOptimized(null);
    }

    function onOptimizeClick (e) {
        e.preventDefault();
        setLoading(true);
        setOptimized(null);
        setLinksGraphMode('plan');
        setError('');

        let start = Date.now();

        // Filter so we're only passing sources for current sku
        let sku_stock = stock.filter(source => source.sku === selectedSku);
        let req_sources = selectedStock.filter(s => sku_stock.find(source => source.id === s));

        DataService.getOptimization(req_sources).then(res => {
            if (res.dynamic_allocation && res.dynamic_allocation.length === 0) {
                setError('Infeasible');
            } else if (res.message) {
                setError(res.message);
            } else {
                let filtered = res.dynamic_allocation.filter(r => {
                    // Don't display it if it has no target, as that would be
                    // considered excess from the optimiser
                    return r.target;
                });

                setOptimized(filtered);
            }
            
            let duration = Date.now() - start;
            setTimeout(() => {
                setLoading(false);
            }, 1000 - duration)
        });
    }

    function onOptimizerSwitch (e) {
        setLinksGraphMode(e.target.checked? 'margin' : 'plan');
    }

    return (
        <div class="App">
            <div class="App-header">
                <span>ai.Retail</span>
                <span>Dynamic Allocation Demo</span>
            </div>
            <div class="App-body">
                <div class="App-bodyInner">
                    <h1>Dynamic Allocation Demo</h1>
                    <div class="App-controls">
                        <span>Selected SKU:</span>
                        <select onChange={onSkuSelect}>
                            {skus.map(s => (
                                <option selected={selectedSku === s}>{s}</option>
                            ))}
                        </select>
                        <form onSubmit={onOptimizeClick}>
                            <button disabled={loading} class="btn btn-primary">Optimize</button>
                        </form> 
                    </div>
                    
                    <div class="App-output">
                        <div class="card shadow">
                            <div class="card-body">
                                <h5 class="card-title">Source DCs</h5>
                                <div style="height: calc(100% - 40px)">
                                    <Table 
                                        columns={SUPPLIER_COLUMNS} 
                                        data={stock.filter(d => d.sku === selectedSku)}
                                        selectable={true} 
                                        selected={selectedStock}
                                        onSelect={onStockSelect}
                                    />
                                </div>
                            </div>
                        </div>
                        <div class="card shadow">
                            <div class="card-body">
                                <h5 class="card-title">Store Demands</h5>
                                <div style="height: calc(100% - 40px)">
                                    <Table 
                                        columns={DEMAND_COLUMNS} 
                                        data={demand.filter(d => d.sku === selectedSku)} 
                                    />
                                </div>
                            </div>
                        </div>
                        <div class="card shadow" style="flex: 1">
                            <div class="card-body">
                                <h5 class="card-title">Optimised Plan</h5>
                                {!loading && optimized && (
                                    <div class="optimized-switch">
                                        <div class="switch text">
                                            <input 
                                                type="checkbox" 
                                                id="switchtxt1"         
                                                onChange={onOptimizerSwitch}
                                                checked={linksGraphMode === 'margin'}
                                            />
                                            <label for="switchtxt1">
                                                <span data-text="Plan"></span>
                                                <span data-text="Margin"></span>
                                            </label>
                                        </div>
                                    </div>
                                )}
                                <div style="height: calc(100% - 40px); display: flex; justify-content: center">
                                    {loading? (
                                        <Loader />
                                    ) : (
                                        optimized? (
                                            <LinksGraph 
                                                demand={demand.filter(d => d.sku === selectedSku)}
                                                margin={links.filter(d => d.sku === selectedSku)} 
                                                optimized={optimized.filter(d => d.sku === selectedSku)}
                                                mode={linksGraphMode}
                                            />
                                        ) : (
                                            error && <div class="optimize-error text-secondary">{error}</div>
                                        )
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}