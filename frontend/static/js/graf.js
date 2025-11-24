// ----- Fetch s timeout -----
async function fetchWithTimeout(url, options = {}, timeout = 5000) {
    return Promise.race([
        fetch(url, options),
        new Promise((_, reject) => setTimeout(() => reject(new Error("Timeout")), timeout))
    ]);
}

// ----- Funkce pro vykreslení grafu -----
async function renderHistoryChart() {
    const container = document.getElementById("historyContainer");
    
    // Vytvoření canvasu pro Chart.js
    container.innerHTML = '<canvas id="historyChart" height="400"></canvas>';
    const ctx = document.getElementById("historyChart").getContext("2d");

    try {
        const data = await fetchWithTimeout("/api/history/last").then(res => res.json());

        // Očekáváme pole objektů {timestamp, temperature, humidity, dewpoint}
        const labels = data.map(d => new Date(d.timestamp).toLocaleString());
        const temperature = data.map(d => d.temperature);
        const humidity = data.map(d => d.humidity);
        const dewpoint = data.map(d => d.dewpoint);

        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Teplota (°C)',
                        data: temperature,
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        yAxisID: 'y1',
                        tension: 0.2
                    },
                    {
                        label: 'Vlhkost (%)',
                        data: humidity,
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        yAxisID: 'y2',
                        tension: 0.2
                    },
                    {
                        label: 'Rosný bod (°C)',
                        data: dewpoint,
                        borderColor: 'rgba(255, 206, 86, 1)',
                        backgroundColor: 'rgba(255, 206, 86, 0.2)',
                        yAxisID: 'y1',
                        tension: 0.2
                    }
                ]
            },
            options: {
                responsive: true,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                stacked: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Historie teploty, vlhkosti a rosného bodu'
                    }
                },
                scales: {
                    y1: {
                        type: 'linear',
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Teplota / Rosný bod (°C)'
                        },
                    },
                    y2: {
                        type: 'linear',
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Vlhkost (%)'
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Čas'
                        }
                    }
                }
            }
        });

    } catch (e) {
        console.error("Chyba při načítání historických dat:", e);
        container.innerHTML = '<p class="text-danger">Historická data nejsou dostupná.</p>';
    }
}

// ----- Inicializace při načtení stránky -----
document.addEventListener("DOMContentLoaded", () => {
    renderHistoryChart();
});
