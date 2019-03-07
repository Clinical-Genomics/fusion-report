// Table functions

var tables = {}
var RANGE = 5;

function register_table(obj) {
    let name = obj['element'].getAttribute('id')
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
let foundFormatter = function(cell, formatterParams){
    return cell.getValue() === 'true' ? '<span class="badge badge-success">Found</span>' : '<span class="badge badge-danger">Not found</span>'
};

let break_ncbiFormatter = function(cell, formatterParams) {
    const row = cell.getData();
    const version = 'hg19', url = 'http://genome.ucsc.edu/cgi-bin';
    let position = parseInt(cell.getValue());
    const start = position - RANGE;
    const end = position + RANGE;
    const chr = row[formatterParams.chr];
    const urlParams = `hgTracks?db=${version}&lastVirtModeType=default&lastVirtModeExtraState=&virtModeType=default&virtMode=0&nonVirtPosition=&position=${chr}%3A${start}-${end}`
    return `<a href="${url}/${urlParams}" target="_blank">${position}</a>`;
}

let break_ensemblFormatter = function(cell, formatterParams) {
    const row = cell.getData();
    const url = 'https://www.ensembl.org'
    let position = parseInt(cell.getValue());
    const start = position - RANGE;
    const end = position + RANGE;
    const transcript = row[formatterParams.transcript];
    const chr = row[formatterParams.chr];
    const urlParams = `Homo_sapiens/Location/View?db=core;r=${chr}:${start}-${end};t=${transcript}`
    return `<a href="${url}/${urlParams}" target="_blank">${position}</a>`;
}

// Table function buttons
function copy_table(name) {
    let table = get_table(name);
    if (table !== undefined) table.copyToClipboard("table");
}

function export_to(name, type) {
    let table = get_table(name);
    if (table !== undefined) table.download(type, `${output_filename}.${type}`)   
}

function match_any(data, value) {
    match = false;
    if (Object.keys(value).length > 1) {
        for (let key in data) {
            if (String(data[key]).toLowerCase().indexOf(value.toLowerCase()) > -1) {
                match = true
            }
        }
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
    var item = document.getElementById(id);
    item.style.display = item.style.display == "none" ? "block" : "none";
}

// Cytoscape helper functions
function export_cytoscape_chart(type, filename) {
    let image = type === 'JPG' ? ppi_obj.jpg() : ppi_obj.png();
    if (image !== undefined) {
        fetch(image)
        .then(res => res.blob())
        .then(blob => {
            var download = document.createElement('a');
            download.href = URL.createObjectURL(blob);
            download.download = `${filename}.${type.toLowerCase()}`;
            download.click();
        });
    }
}