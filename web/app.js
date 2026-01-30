// Network Discovery Dashboard JavaScript

// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Cytoscape instance
let cy = null;
let topologyData = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeCytoscape();
    loadTopology();
});

// Initialize Cytoscape
function initializeCytoscape() {
    cy = cytoscape({
        container: document.getElementById('topology'),

        style: [
            {
                selector: 'node',
                style: {
                    'label': 'data(label)',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'background-color': function(ele) {
                        const type = ele.data('type');
                        if (type === 'switch') return '#3498db';
                        if (type === 'router') return '#e74c3c';
                        return '#95a5a6';
                    },
                    'width': 40,
                    'height': 40,
                    'font-size': '12px',
                    'color': '#fff',
                    'text-outline-width': 2,
                    'text-outline-color': '#1a1a2e'
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#1a5490',
                    'target-arrow-color': '#1a5490',
                    'curve-style': 'bezier',
                    'label': function(ele) {
                        const src = ele.data('source_interface');
                        return src ? abbreviateInterface(src) : '';
                    },
                    'font-size': '8px',
                    'color': '#95a5a6',
                    'text-rotation': 'autorotate'
                }
            },
            {
                selector: ':selected',
                style: {
                    'background-color': '#f39c12',
                    'line-color': '#f39c12',
                    'target-arrow-color': '#f39c12',
                    'border-width': 3,
                    'border-color': '#f39c12'
                }
            }
        ],

        layout: {
            name: 'cose',
            animate: true,
            animationDuration: 500
        }
    });

    // Add event listeners
    cy.on('tap', 'node', function(evt) {
        const node = evt.target;
        showDeviceDetails(node.data());
    });

    cy.on('tap', function(evt) {
        if (evt.target === cy) {
            hideDeviceDetails();
        }
    });
}

// Load topology from API
async function loadTopology() {
    try {
        showLoading(true);

        const response = await fetch(`${API_BASE_URL}/topology`);
        if (!response.ok) throw new Error('Failed to load topology');

        topologyData = await response.json();

        // Update stats
        document.getElementById('device-count').textContent = topologyData.nodes.length;
        document.getElementById('connection-count').textContent = topologyData.edges.length;

        // Build graph
        buildGraph(topologyData);

        showLoading(false);
    } catch (error) {
        console.error('Error loading topology:', error);
        showLoading(false);
        alert('Failed to load topology. Make sure the API server is running.');
    }
}

// Build Cytoscape graph from data
function buildGraph(data) {
    cy.elements().remove();

    // Add nodes
    data.nodes.forEach(node => {
        cy.add({
            group: 'nodes',
            data: {
                id: node.id,
                label: node.label,
                type: node.type,
                ip: node.ip,
                model: node.model,
                ios_version: node.ios_version,
                interfaces_count: node.interfaces_count
            }
        });
    });

    // Add edges
    data.edges.forEach(edge => {
        cy.add({
            group: 'edges',
            data: {
                id: `${edge.source}-${edge.target}`,
                source: edge.source,
                target: edge.target,
                source_interface: edge.source_interface,
                dest_interface: edge.dest_interface,
                link_type: edge.link_type
            }
        });
    });

    // Apply layout
    cy.layout({
        name: 'cose',
        animate: true,
        animationDuration: 500,
        nodeRepulsion: 4000,
        idealEdgeLength: 100
    }).run();
}

// Show device details in sidebar
function showDeviceDetails(data) {
    const panel = document.getElementById('device-panel');
    const details = document.getElementById('device-details');

    let html = `
        <div class="detail-row">
            <span class="detail-label">Hostname:</span>
            <span class="detail-value">${data.label}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">IP Address:</span>
            <span class="detail-value">${data.ip || 'N/A'}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Type:</span>
            <span class="detail-value">${data.type || 'unknown'}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Model:</span>
            <span class="detail-value">${data.model || 'N/A'}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">IOS Version:</span>
            <span class="detail-value">${data.ios_version || 'N/A'}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Interfaces:</span>
            <span class="detail-value">${data.interfaces_count || 0}</span>
        </div>
    `;

    details.innerHTML = html;
    panel.style.display = 'block';
}

// Hide device details
function hideDeviceDetails() {
    document.getElementById('device-panel').style.display = 'none';
}

// Search for MAC address
async function searchMAC() {
    const input = document.getElementById('mac-search');
    const mac = input.value.trim();

    if (!mac) {
        alert('Please enter a MAC address');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/search/mac/${encodeURIComponent(mac)}`);
        const data = await response.json();

        const resultsDiv = document.getElementById('search-results');

        if (!data.found) {
            resultsDiv.innerHTML = '<div class="error">MAC address not found</div>';
            return;
        }

        let html = '<div class="success">Found MAC address!</div>';
        data.locations.forEach(loc => {
            html += `
                <div class="search-result-item">
                    <strong>${loc.device}</strong><br>
                    Interface: ${loc.interface}<br>
                    VLAN: ${loc.vlan_id}<br>
                    Type: ${loc.type}
                </div>
            `;

            // Highlight node in graph
            const node = cy.getElementById(loc.device);
            if (node) {
                cy.elements().unselect();
                node.select();
                cy.animate({
                    center: { eles: node },
                    zoom: 2
                }, {
                    duration: 500
                });
            }
        });

        resultsDiv.innerHTML = html;
    } catch (error) {
        console.error('Error searching MAC:', error);
        document.getElementById('search-results').innerHTML =
            '<div class="error">Search failed. Please try again.</div>';
    }
}

// Search for device
async function searchDevice() {
    const input = document.getElementById('device-search');
    const query = input.value.trim();

    if (!query) {
        alert('Please enter a device hostname or IP');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/search/device?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        const resultsDiv = document.getElementById('search-results');

        if (!data.found) {
            resultsDiv.innerHTML = '<div class="error">Device not found</div>';
            return;
        }

        let html = '<div class="success">Found device(s)!</div>';
        data.devices.forEach(device => {
            html += `
                <div class="search-result-item">
                    <strong>${device.hostname}</strong><br>
                    IP: ${device.ip_address}<br>
                    Type: ${device.device_type || 'unknown'}<br>
                    Model: ${device.model || 'N/A'}
                </div>
            `;

            // Highlight node in graph
            const node = cy.getElementById(device.hostname);
            if (node) {
                cy.elements().unselect();
                node.select();
                cy.animate({
                    center: { eles: node },
                    zoom: 2
                }, {
                    duration: 500
                });
            }
        });

        resultsDiv.innerHTML = html;
    } catch (error) {
        console.error('Error searching device:', error);
        document.getElementById('search-results').innerHTML =
            '<div class="error">Search failed. Please try again.</div>';
    }
}

// Refresh topology
function refreshTopology() {
    loadTopology();
}

// Fit graph to screen
function fitGraph() {
    cy.fit();
}

// Change layout
function changeLayout() {
    const layout = document.getElementById('layout-select').value;
    cy.layout({
        name: layout,
        animate: true,
        animationDuration: 500
    }).run();
}

// Export topology as JSON
function exportTopology() {
    if (!topologyData) {
        alert('No topology data to export');
        return;
    }

    const dataStr = JSON.stringify(topologyData, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});

    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'topology.json';
    link.click();

    URL.revokeObjectURL(url);
}

// Show/hide loading indicator
function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
}

// Abbreviate interface name
function abbreviateInterface(name) {
    const abbr = {
        'GigabitEthernet': 'Gi',
        'TenGigabitEthernet': 'Te',
        'FastEthernet': 'Fa'
    };

    for (const [full, short] of Object.entries(abbr)) {
        if (name.startsWith(full)) {
            return name.replace(full, short);
        }
    }

    return name;
}

// Allow Enter key for search
document.getElementById('mac-search').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') searchMAC();
});

document.getElementById('device-search').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') searchDevice();
});
