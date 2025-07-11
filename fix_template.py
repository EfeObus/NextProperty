# This script will fix the analytics_insights.html template by replacing the JavaScript section

import re

# Read the current template
with open('/Users/efeobukohwo/Desktop/Nextproperty Real Estate/app/templates/dashboard/analytics_insights.html', 'r') as f:
    content = f.read()

# Find the start and end of the JavaScript section
js_start = content.find('{% block extra_js %}')
js_end = content.find('{% endblock %}', js_start) + len('{% endblock %}')

if js_start == -1 or js_end == -1:
    print("Could not find JavaScript section")
    exit(1)

# Extract the part before and after the JavaScript section
before_js = content[:js_start]
after_js = content[js_end:]

# Create the new JavaScript section
new_js = '''{% block extra_js %}
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

{% if feature_analysis and feature_analysis.success %}
<script>
console.log('Initializing feature importance charts...');

// Prepare data from server using safe JSON encoding
const featureLabels = {{ feature_analysis.top_10_features | map(attribute='feature') | list | tojson }};
const featureData = {{ feature_analysis.top_10_features | map(attribute='importance_percent') | list | tojson }};
const allFeatureLabels = {{ feature_analysis.all_features | map(attribute='feature') | list | tojson }};
const allFeatureData = {{ feature_analysis.all_features | map(attribute='importance_percent') | list | tojson }};
const categoryLabels = {{ feature_analysis.category_importance | map(attribute='category') | list | tojson }};
const categoryData = {{ feature_analysis.category_importance | map(attribute='importance_percent') | list | tojson }};

console.log('Data loaded - Features:', featureLabels.length, 'Categories:', categoryLabels.length);

// Global chart variables
let featureChart = null;
let categoryChart = null;
let currentView = 'top10';

// Generate colors
function generateColors(count) {
    const colors = [];
    for (let i = 0; i < count; i++) {
        const hue = (i * 137.508) % 360;
        colors.push(`hsla(${hue}, 70%, 60%, 0.8)`);
    }
    return colors;
}

// Initialize Feature Chart
function initFeatureChart() {
    const canvas = document.getElementById('featureChart');
    if (!canvas) {
        console.error('Feature chart canvas not found');
        return;
    }

    console.log('Creating feature chart...');
    
    const colors = generateColors(featureLabels.length);

    featureChart = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: featureLabels.slice(0, 15),
            datasets: [{
                label: 'Importance %',
                data: featureData.slice(0, 15),
                backgroundColor: colors,
                borderColor: colors.map(c => c.replace('0.8', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Top 15 Features by Importance',
                    font: { size: 16 }
                },
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y.toFixed(2) + '% importance';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(1) + '%';
                        }
                    },
                    title: { display: true, text: 'Importance (%)' }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                        font: { size: 10 }
                    },
                    title: { display: true, text: 'Features' }
                }
            }
        }
    });

    console.log('Feature chart created successfully');
}

// Initialize Category Chart
function initCategoryChart() {
    const canvas = document.getElementById('categoryChart');
    if (!canvas) {
        console.error('Category chart canvas not found');
        return;
    }

    console.log('Creating category chart...');

    const categoryColors = [
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 99, 132, 0.8)',
        'rgba(255, 205, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)'
    ];

    categoryChart = new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: categoryLabels,
            datasets: [{
                data: categoryData,
                backgroundColor: categoryColors,
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Feature Categories by Total Importance'
                },
                legend: {
                    display: true,
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed.toFixed(1) + '%';
                        }
                    }
                }
            }
        }
    });

    console.log('Category chart created successfully');
}

// Show all 26 features
function showAllFeatures() {
    if (!featureChart) return;
    
    console.log('Showing all features...');
    
    const colors = generateColors(allFeatureLabels.length);
    
    featureChart.data.labels = allFeatureLabels;
    featureChart.data.datasets[0].data = allFeatureData;
    featureChart.data.datasets[0].backgroundColor = colors;
    featureChart.data.datasets[0].borderColor = colors.map(c => c.replace('0.8', '1'));
    featureChart.options.plugins.title.text = 'All 26 Features by Importance';
    featureChart.update();
    currentView = 'all26';
}

// Show category chart
function showCategoryChart() {
    if (!featureChart) return;
    
    console.log('Switching to category view...');
    
    featureChart.destroy();
    const canvas = document.getElementById('featureChart');
    
    featureChart = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: categoryLabels,
            datasets: [{
                label: 'Category Importance %',
                data: categoryData,
                backgroundColor: [
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(255, 205, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)',
                    'rgba(255, 159, 64, 0.8)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Feature Categories by Total Importance',
                    font: { size: 16 }
                },
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(1) + '%';
                        }
                    }
                }
            }
        }
    });
    
    currentView = 'category';
}

// Export functionality (simplified)
function exportCharts() {
    alert('Export functionality available! Charts can be saved by right-clicking and selecting "Save image as..."');
}

function exportFeatureData() {
    // Simple CSV export
    let csvContent = "Rank,Feature,Category,Importance\\n";
    // This would need to be populated from the template data
    alert('CSV export functionality coming soon!');
}

// Debug function
function debugCharts() {
    const debugInfo = document.getElementById('debugInfo');
    if (debugInfo) {
        debugInfo.style.display = debugInfo.style.display === 'none' ? 'block' : 'none';
        
        const debugData = document.getElementById('debugData');
        if (debugData) {
            const debug = {
                chartsInitialized: {
                    feature: !!featureChart,
                    category: !!categoryChart
                },
                dataLoaded: {
                    features: featureLabels.length,
                    categories: categoryLabels.length
                },
                currentView: currentView
            };
            debugData.textContent = JSON.stringify(debug, null, 2);
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing charts...');
    setTimeout(() => {
        initFeatureChart();
        initCategoryChart();
    }, 100);
});
</script>
{% else %}
<script>
console.log('Feature analysis not available');
</script>
{% endif %}

{% endblock %}'''

# Combine the parts
new_content = before_js + new_js + after_js

# Write the fixed template
with open('/Users/efeobukohwo/Desktop/Nextproperty Real Estate/app/templates/dashboard/analytics_insights_fixed.html', 'w') as f:
    f.write(new_content)

print("Fixed template created as analytics_insights_fixed.html")
