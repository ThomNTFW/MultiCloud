import './LinksGraph.scss';

const GREEN = '#19a954';
const RED = '#fa4647';
const ORANGE = '#fa821f';
const EMPTY = '#4e585b';
const NEUTRAL = '#6c787f';

let CANVAS_GRADIENT = (function () {
    let canvas = document.createElement('canvas');
    canvas.width = 101;
    canvas.height = 1;
    let ctx = canvas.getContext('2d');
    let gradient = ctx.createLinearGradient(0, 0, 101, 0);
    gradient.addColorStop(0, RED);
    gradient.addColorStop(1, GREEN);
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 101, 1);

    return p => {
        let c = ctx.getImageData(Math.round(p), 0, 1, 1);
        return `rgb(${c.data[0]}, ${c.data[1]}, ${c.data[2]})`
    }
})();

function calculateMarginColor (min, max, value) {
    let p = (value - min) / (max - min);
    return CANVAS_GRADIENT(p *  100);
}

export default function LinksGraph (props) {
    let sources = [...new Set(props.margin.map(d => d.source))];
    let targets = [...new Set(props.margin.map(d => d.target))];
    let margin_min = Math.min(...props.margin.map(d => parseFloat(d.margin)));
    let margin_max = Math.max(...props.margin.map(d => parseFloat(d.margin)));
    let { mode, optimized, demand }  = props;

    return (
        <div class="LinksGraph">
            <table>
                <tr>
                    <td></td>
                    {targets.map(t => <td class="target">{t}</td>)}
                </tr>
                {sources.map(s => (
                    <tr>
                        <td class="source">{s}</td>
                        {targets.map(t => {
                            let value, color, opacity;
                            let plan_match = optimized.find(d => d.source === s && d.target === t);

                            if (mode === 'plan') {
                                value = plan_match? plan_match.transfer : '-';
                                color = plan_match? NEUTRAL : EMPTY;
                                opacity = 1;
                            } else if (mode === 'margin') {
                                value = props.margin.find(d => d.source === s && d.target === t).margin;
                                color = calculateMarginColor(margin_min, margin_max, parseFloat(value));
                                opacity = plan_match? 1 : 0.5;
                            }

                            return <td class="value" style={`background-color: ${color}; opacity: ${opacity}`}>{value}</td>
                        })}
                    </tr>
                ))}
                <tr class="total-row" style={{
                    'opacity': mode === 'plan'? 1 : 0.25
                }}>
                    <td class="total">Supplied / Demand</td>
                    {targets.map(t => {
                        let supplied = optimized.filter(d => d.source && d.target === t).reduce((acc, val) => acc + val.transfer, 0);
                        let demanded = demand.find(d => d.target === t).demand;
                        let color = supplied === demanded? GREEN : (supplied === 0? RED : ORANGE);

                        return <td class="value" style={`background-color: ${color}`}>{supplied}/{demanded}</td>
                    })}
                </tr>
            </table>
        </div>
    )
}