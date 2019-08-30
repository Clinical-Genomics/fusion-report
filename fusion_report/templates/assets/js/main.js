// Table functions

let tables = {};
const RANGE = 5;

function registerTable(obj) {
    let name = obj.element.getAttribute("id");
    if (!tables.hasOwnProperty(name)) {
        tables[name] = obj;
    } else {
        console.warn(
            `Table with name: ${name} was already register. Please rename your table id.`
        );
    }
}

function getTable(name) {
    return (name === "" || name === undefined) ? undefined : tables[name];
}

// Table formatters
let foundDBFormatter = function(cell, formatterParams) {
    let newCell = "";
    let items = cell.getValue();
    if (items.length === 0) {
        newCell = "<span class='badge badge-danger'>Not found</span>";
    } else {
        items.forEach(function (item) {
            newCell += `<span class="badge badge-${formatterParams[item]}">
                            <span class="label">${item[0]}<span class="d-none d-xl-inline">${item.substr(1)}</span></span>
                        </span>&nbsp;`;
        });
    }
    return newCell;
};

let breakNcbiFormatter = function(cell, formatterParams) {
    const row = cell.getData();
    const version = "hg19", url = "http://genome.ucsc.edu/cgi-bin";
    let position = parseInt(cell.getValue());
    const start = position - RANGE;
    const end = position + RANGE;
    const chr = row[formatterParams.chr];
    const urlParams = `hgTracks?db=${version}&lastVirtModeType=default&lastVirtModeExtraState=&virtModeType=default&virtMode=0&nonVirtPosition=&position=${chr}%3A${start}-${end}`;
    return `<a href="${url}/${urlParams}" target="_blank" data-toggle="tooltip" data-placement="top" title="Open in UCSC browser">${position}</a>`;
};

let breakEnsemblFormatter = function(cell, formatterParams) {
    const row = cell.getData(), url = "https://www.ensembl.org";
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
    let progressValue = ("delimiter" in formatterParams ? value / formatterParams.delimiter : value) * 100;
    let style = "style" in formatterParams ? formatterParams.style : "bg-primary";
    return `<div class="progress">
                <div class="progress-bar ${style}" role="progressbar" style="width: ${progressValue}%;" 
                    aria-valuenow="${progressValue}" aria-valuemin="0" aria-valuemax="100">
                    ${value}
                </div>
            </div>`;
};

let linkFormatter = function(cell, formatterParams) {
    let value = cell.getValue();
    let target = formatterParams.target ? formatterParams.target : "_blank";
    return `<a href="${formatterParams.url}/${value}" target="${target}" data-toggle="tooltip" data-placement="top" title="${formatterParams.title}">${value}</a>`;
};

// Table function buttons
function copyTable(name) {
    let table = getTable(name);
    if (table !== undefined) { table.copyToClipboard("table"); }
}

function exportTo(name, type) {
    let table = getTable(name);
    if (table !== undefined) { table.download(type, `${name}.${type}`); }
}

function matchAny(data, value) {
    let match = false;
    if (Object.keys(value).length > 1) {
        Object.values(data).forEach(function(item) {
            if (String(item).toLowerCase().indexOf(value.toLowerCase()) > -1) {
                match = true;
            }
        });
        return match;
    }
    return true;
}

// Table inputs
function filterBy(name, field, obj) {
    let table = getTable(name);
    if (table !== undefined && obj.value !== undefined) {
        if (field === "*") {
            table.setFilter(matchAny, obj.value);
        } else {
            table.setFilter(field, "like", obj.value);
        }
    }
}

// Helpers
function toggleView(id) {
    let item = document.getElementById(id);
    item.style.display = item.style.display === "none" ? "block" : "none";
}

function toggleCard(currentLink, id) {
    let prevActive = document.getElementsByClassName("card-header")[0].querySelector(".active");
    prevActive.className = "nav-link";
    currentLink.className = "nav-link active";
    
    let allCards = document.getElementsByClassName("card-body");
    Array.from(allCards).map(function(card) {
        card.style.display = "none";
    });
    document.getElementById(id).style.display = "block";
}

// Cytoscape helper functions
function exportCytoscapeChart(type, filename) {
    let image = type === "JPG" ? ppiObject.jpg() : ppiObject.png();
    if (image !== undefined) {
        fetch(image)
        .then((res) => res.blob())
        .then((blob) => {
            let download = document.createElement("a");
            download.href = URL.createObjectURL(blob);
            download.download = `${filename}.${type.toLowerCase()}`;
            download.click();
        });
    }
}