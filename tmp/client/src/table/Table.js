import { useState, useEffect } from 'preact/hooks';
import './Table.scss';

export default function Table (props) {
    let [ sortData, setSortData ] = useState([]);
    let [ sortColumn, setSortColumn ] = useState('');
    let [ sortOrder, setSortOrder ] = useState('');

    function onSort (property) {
        if (sortColumn === property) {
            setSortOrder(sortOrder === 'asc'? 'desc' : 'asc');
        } else {
            setSortColumn(property);
            setSortOrder('asc');
        }

        setSortData(sortData.slice().sort((a, b) => {
            a = a[property];
            b = b[property];
            let result = typeof a === 'string'? a.localeCompare(b) : (a - b);
            return result * (sortOrder === 'asc'? 1 : -1);
        }));
    }

    useEffect(() => {
        setSortData(props.data);
        setSortColumn('');
        setSortOrder('');
    }, [ props.data ]);
    
    return (
        <div class="Table">
            <table class="table table-hover">
                <thead>
                    <tr>
                        {props.selectable && <th></th>}
                        {props.columns.map(c => (
                            <th
                                data-sort={c.property === sortColumn}
                                data-order={sortOrder}
                                onClick={() => onSort(c.property)}
                            >{c.title}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {sortData && sortData.map(d => (
                        <tr onClick={props.selectable && (() => props.onSelect(d.id))}>
                            {props.selectable && (
                                <td>
                                    <div class="custom-control custom-checkbox">
                                        <input 
                                            id={'cb-' + d.id}
                                            type="checkbox" 
                                            data-checked={props.selected.findIndex(s => s === d.id) > -1}
                                            class="custom-control-input" 
                                            checked={props.selected.findIndex(s => s === d.id) > -1} 
                                            onChange={() => props.onSelect(d.id)}
                                        />
                                        <label class="custom-control-label" for={'cb-' + d.id} />
                                    </div>
                                </td>
                            )}
                            {props.columns.map(c => (
                                props.cell? props.cell(d[c.property], d) : <td>{d[c.property]}</td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}