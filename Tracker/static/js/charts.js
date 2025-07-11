// ✅ Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (const cookie of cookies) {
            const trimmed = cookie.trim();
            if (trimmed.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// ✅ Fetch chart data
fetch('/api/chart-data/', {
    method: 'GET',
    headers: {
        'X-CSRFToken': csrftoken
    },
    credentials: 'include'
})
.then(response => response.json())
.then(data => {
    const ctxBar = document.getElementById('barChart').getContext('2d');
    const ctxPie = document.getElementById('pieChart').getContext('2d');

    // Bar Chart: Monthly Totals
    new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: data.month_labels,
            datasets: [{
                label: 'Monthly Expenses',
                data: data.monthly_totals,
                backgroundColor: 'rgba(99, 102, 241, 0.6)',
                borderColor: 'rgba(99, 102, 241, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Pie Chart: Category Totals
    new Chart(ctxPie, {
        type: 'pie',
        data: {
            labels: data.category_labels,
            datasets: [{
                label: 'By Category',
                data: data.category_totals,
                backgroundColor: [
                    '#4f46e5', '#16a34a', '#facc15', '#f97316',
                    '#dc2626', '#14b8a6', '#8b5cf6', '#f43f5e'
                ]
            }]
        },
        options: {
            responsive: true
        }
    });
})
.catch(error => console.error('Chart fetch error:', error));