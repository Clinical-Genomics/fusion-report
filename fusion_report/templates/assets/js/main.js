// Table functions

let tables = {};
const RANGE = 5;

function register_table(obj) {
    let name = obj['element'].getAttribute('id');
    if (tables[name] === undefined) {
        tables[name] = obj;
    } else {
        console.log(`Table with name: ${name} was already register. Please rename your table id.`)
    }
}

function get_table(name) {
    return (name === "" || name === undefined) ? undefined : tables[name];
}

// Table formatters
let foundDBFormatter = function(cell, formatterParams) {
    let new_cell = '';
    let items = cell.getValue();
    if (items.length === 0) {
        new_cell = '<span class="badge badge-danger">Not found</span>'
    } else {
        items.forEach(function (item) {
            new_cell += `<span class="badge badge-${formatterParams[item]}">
                            <span class="label">${item[0]}<span class="d-none d-xl-inline">${item.substr(1)}</span></span>
                        </span>&nbsp;`
        });
    }
    return new_cell
};

let break_ncbiFormatter = function(cell, formatterParams) {
    const row = cell.getData();
    const version = 'hg19', url = 'http://genome.ucsc.edu/cgi-bin';
    let position = parseInt(cell.getValue());
    const start = position - RANGE;
    const end = position + RANGE;
    const chr = row[formatterParams.chr];
    const urlParams = `hgTracks?db=${version}&lastVirtModeType=default&lastVirtModeExtraState=&virtModeType=default&virtMode=0&nonVirtPosition=&position=${chr}%3A${start}-${end}`;
    return `<a href="${url}/${urlParams}" target="_blank" data-toggle="tooltip" data-placement="top" title="Open in UCSC browser">${position}</a>`;
};

let break_ensemblFormatter = function(cell, formatterParams) {
    const row = cell.getData();
    const url = 'https://www.ensembl.org';
    let position = parseInt(cell.getValue());
    const start = position - RANGE;
    const end = position + RANGE;
    const transcript = row[formatterParams.transcript];
    const chr = row[formatterParams.chr];
    const urlParams = `Homo_sapiens/Location/View?db=core;r=${chr}:${start}-${end};t=${transcript}`;
    return `<a href="${url}/${urlParams}" target="_blank" data-toggle="tooltip" data-placement="top" title="Open in Ensembl genome browser">${position}</a>`;
};

let progressFormatter = function(cell, formatterParams) {
    let value = cell.getValue();
    let progress_value = ('delimiter' in formatterParams ? value / formatterParams.delimiter : value) * 100;
    let style = 'style' in formatterParams ? formatterParams.style : 'bg-primary';
    return `<div class="progress">
                <div class="progress-bar ${style}" role="progressbar" style="width: ${progress_value}%;" 
                    aria-valuenow="${progress_value}" aria-valuemin="0" aria-valuemax="100">
                    ${value}
                </div>
            </div>`
};

let linkFormatter = function(cell, formatterParams) {
    let value = cell.getValue();
    let target = formatterParams.target ? formatterParams.target : "_blank";
    return `<a href="${formatterParams.url}/${value}" target="${target}" data-toggle="tooltip" data-placement="top" title="${formatterParams.title}">${value}</a>`;
};

// Table function buttons
function copy_table(name) {
    let table = get_table(name);
    if (table !== undefined) table.copyToClipboard("table");
}

function export_to(name, type) {
    let table = get_table(name);
    if (table !== undefined) table.download(type, `${name}.${type}`)   
}

function match_any(data, value) {
    let match = false;
    if (Object.keys(value).length > 1) {
        Object.values(data).forEach(function(item) {
            if (String(item).toLowerCase().indexOf(value.toLowerCase()) > -1) {
                match = true
            }
        });
        return match;
    }
    return true;
}

// Table inputs
function filter_by(name, field, obj) {
    let table = get_table(name);
    if (table !== undefined && obj.value !== undefined) {
        if (field === '*') {
            table.setFilter(match_any, obj.value)
        } else {
            table.setFilter(field, 'like', obj.value);
        }
    }
}

// Helpers
function toggle_view(id) {
    let item = document.getElementById(id);
    item.style.display = item.style.display === "none" ? "block" : "none";
}

function toggle_card(current_link, id) {
    let prev_active = document.getElementsByClassName('card-header')[0].querySelector('.active');
    prev_active.className = 'nav-link';
    current_link.className = 'nav-link active';
    
    let all_cards = document.getElementsByClassName('card-body');
    Array.from(all_cards).map(function(card) {
        card.style.display = 'none'
    });
    document.getElementById(id).style.display = 'block';
}

// Cytoscape helper functions
function export_cytoscape_chart(type, filename) {
    let image = type === 'JPG' ? ppi_obj.jpg() : ppi_obj.png();
    if (image !== undefined) {
        fetch(image)
        .then(res => res.blob())
        .then(blob => {
            let download = document.createElement('a');
            download.href = URL.createObjectURL(blob);
            download.download = `${filename}.${type.toLowerCase()}`;
            download.click();
        });
    }
}