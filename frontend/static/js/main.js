// ----- Přepínač motivu s uložením do localStorage -----
const themeToggle = document.getElementById("themeToggle");
const themeIcon = document.getElementById("themeIcon");
const htmlTag = document.documentElement;

function setTheme(theme) {
    htmlTag.setAttribute("data-bs-theme", theme);
    themeIcon.className = theme === "dark" ? "bi bi-brightness-high" : "bi bi-moon-stars";
    localStorage.setItem("theme", theme);
}

document.addEventListener("DOMContentLoaded", () => {
    const savedTheme = localStorage.getItem("theme") || "light";
    setTheme(savedTheme);
});

themeToggle.addEventListener("click", () => {
    const current = htmlTag.getAttribute("data-bs-theme");
    setTheme(current === "light" ? "dark" : "light");
});

// ----- Fetch s timeout -----
async function fetchWithTimeout(url, options = {}, timeout = 5000) {
    return Promise.race([
        fetch(url, options),
        new Promise((_, reject) => setTimeout(() => reject(new Error("Timeout")), timeout))
    ]);
}

// ----- Aktualizace hodnot z API -----
const elements = {
    temperature: document.querySelector("#temperature .card-text"),
    pressure: document.querySelector("#pressure .card-text"),
    humidity: document.querySelector("#humidity .card-text"),
    dewPoint: document.querySelector("#dewPoint .card-text"),
    pragueTemp: document.querySelector("#outTemp .card-text")
};

async function updateWeatherValues() {
    try {
        const data = await fetchWithTimeout("/api/temp/now").then(res => res.json());

        if (data.temperature !== undefined) elements.temperature.textContent = data.temperature.toFixed(1) + " °C";
        if (data.pressure !== undefined) elements.pressure.textContent = data.pressure + " hPa";
        if (data.humidity !== undefined) elements.humidity.textContent = data.humidity + " %";
        if (data.dew_point !== undefined) elements.dewPoint.textContent = data.dew_point + " °C";
        if (data.out_temp !== undefined) elements.pragueTemp.textContent = data.out_temp.toFixed(1) + " °C";
    } catch (e) {
        console.error("Chyba při načítání hodnot:", e);
        for (let key in elements) elements[key].textContent = "Nedostupné";
    }
}

// ----- Switchy -----
const switches = {
    heating: document.getElementById("heating"),
    automat: document.getElementById("automat")
};

async function getSwitchState(name) {
    try {
        const data = await fetchWithTimeout(`/api/switch/get/${name}`).then(res => res.json());
        if (data.state !== undefined) {
            switches[name].checked = data.state;
            switches[name].parentElement.parentElement.classList.toggle("active-switch", data.state);
        }
    } catch (e) {
        console.error(`Chyba při GET switche ${name}:`, e);
        switches[name].checked = false;
        switches[name].parentElement.parentElement.classList.remove("active-switch");
    }
}

async function setSwitchState(name, state) {
    try {
        const response = await fetch(`/api/switch/set/${name}`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ state })
        });
        const data = await response.json();
        if (!data.ok) throw new Error("API rejected switch update");
        switches[name].parentElement.parentElement.classList.toggle("active-switch", state);
        return true;
    } catch (e) {
        console.error(`Chyba při POST switche ${name}:`, e);
        return false;
    }
}

// ----- Slider desire_temp -----
const slider = document.getElementById("desire_temp");
const sliderValue = document.getElementById("sliderValue");

async function getSliderValue() {
    try {
        const data = await fetchWithTimeout("/api/slider/get/desire_temp").then(res => res.json());
        if (data.state !== undefined) {
            slider.value = data.state;
            sliderValue.textContent = data.state;
        }
    } catch (e) {
        console.error("Chyba při GET slideru:", e);
        slider.value = 20; // fallback hodnota
        sliderValue.textContent = 20;
    }
}

async function setSliderValue(value) {
    try {
        const response = await fetch("/api/slider/set/desire_temp", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ state: parseFloat(value) })
        });
        const data = await response.json();
        if (!data.ok) throw new Error("API rejected slider update");
        sliderValue.textContent = value;
        return true;
    } catch (e) {
        console.error("Chyba při POST slideru:", e);
        return false;
    }
}

// ----- Inicializace -----
document.addEventListener("DOMContentLoaded", () => {
    updateWeatherValues();
    setInterval(updateWeatherValues, 5000);

    // Inicializace switchů
    Object.keys(switches).forEach(getSwitchState);
    Object.keys(switches).forEach(name => {
        switches[name].addEventListener("change", async () => {
            const newState = switches[name].checked;
            const ok = await setSwitchState(name, newState);
            if (!ok) switches[name].checked = !newState;
        });
    });

    // Inicializace slideru
    getSliderValue();
    slider.addEventListener("input", (e) => {
        sliderValue.textContent = e.target.value;
    });
    slider.addEventListener("change", async (e) => {
        const newValue = e.target.value;
        const ok = await setSliderValue(newValue);
        if (!ok) getSliderValue(); // fallback na poslední známou hodnotu
    });

    // Polling pro switch a slider každých 5s
    setInterval(() => {
        Object.keys(switches).forEach(getSwitchState);
        getSliderValue();
    }, 5000);
});
