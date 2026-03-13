let groupsData = {};
const regionTabsContainer = document.getElementById('region-tabs');
const sectionsContainer = document.getElementById('sections-container');

const regionOrder = ["EN", "CN", "JP", "KR", "TW"];
let currentRegion = "JP"; // Default

const typeNames = {
    "1": "Main Story",
    "2": "Event",
    "3": "Character Story",
    "non-archived": "Non Archived"
};

const subtypeNames = {
    "2": { // Subtypes for Type 2 (Event)
        "1": "Event (EX)",
        "2": "Special (SP)",
        "3": "Permanent (Daily Life)"
    }
};

let availableRegions = [];

async function fetchGroupsData() {
    try {
        const response = await fetch('data/groups.json');
        groupsData = await response.json();

        let allRegionsSet = new Set();
        Object.values(groupsData).forEach(data => {
            Object.keys(data.titles).forEach(r => allRegionsSet.add(r));
        });

        availableRegions = Array.from(allRegionsSet).sort((a, b) => {
            let ia = regionOrder.indexOf(a), ib = regionOrder.indexOf(b);
            if (ia === -1) ia = 99; if (ib === -1) ib = 99;
            return ia - ib;
        });

        init();
    } catch (e) {
        console.error("Failed to load global story index", e);
        sectionsContainer.innerHTML = "<p>Error loading story list. Ensure you are running a local web server (e.g., python -m http.server).</p>";
    }
}

function init() {
    const savedRegion = localStorage.getItem('selectedRegion');
    if (savedRegion && availableRegions.includes(savedRegion)) {
        currentRegion = savedRegion;
    } else if (availableRegions.length > 0) {
        if (availableRegions.includes("EN")) currentRegion = "EN";
        else if (availableRegions.includes("JP")) currentRegion = "JP";
        else currentRegion = availableRegions[0];
    }
    renderRegionTabs();
    selectRegion(currentRegion);
}

function renderRegionTabs() {
    regionTabsContainer.innerHTML = '';
    availableRegions.forEach(region => {
        const btn = document.createElement('button');
        btn.className = 'tab-btn';
        btn.textContent = region;
        btn.onclick = () => selectRegion(region);
        if (region === currentRegion) btn.classList.add('active');
        regionTabsContainer.appendChild(btn);
    });
}

function selectRegion(region) {
    currentRegion = region;
    localStorage.setItem('selectedRegion', region);

    Array.from(regionTabsContainer.children).forEach(btn => {
        btn.classList.toggle('active', btn.textContent === region);
    });

    renderGrid();
}

function renderGrid() {
    sectionsContainer.innerHTML = '';

    let typeMap = {};
    Object.keys(groupsData).forEach(g_id => {
        const data = groupsData[g_id];
        const t = data.type;
        if (!typeMap[t]) typeMap[t] = [];
        typeMap[t].push(g_id);
    });

    let sortedTypes = Object.keys(typeMap).sort((a, b) => {
        // if (a === "non-archived") return 1;
        // if (b === "non-archived") return -1;
        return parseInt(a) - parseInt(b);
    });

    sortedTypes.forEach(type => {
        const section = document.createElement("div");
        section.className = "type-section";

        const header = document.createElement("div");
        header.className = "type-header";
        header.textContent = typeNames[type] || `${type}`;
        section.appendChild(header);

        if (type === "2") {
            // Group by subtype for type 2
            let subtypeMap = {};
            typeMap[type].forEach(g_id => {
                const sub = groupsData[g_id].subtype || "0";
                if (!subtypeMap[sub]) subtypeMap[sub] = [];
                subtypeMap[sub].push(g_id);
            });

            // Sort subtypes numerically
            let sortedSubtypes = Object.keys(subtypeMap).sort((a, b) => parseInt(a) - parseInt(b));

            sortedSubtypes.forEach(sub => {
                const subHeader = document.createElement("div");
                subHeader.className = "subtype-header";
                subHeader.textContent = (subtypeNames[type] && subtypeNames[type][sub]) || `Subtype ${sub}`;
                section.appendChild(subHeader);

                const grid = document.createElement("div");
                grid.className = "grid-container";

                let sortedGroupIds = subtypeMap[sub].sort((a, b) => parseInt(a) - parseInt(b));
                renderCardsToGrid(sortedGroupIds, grid);
                section.appendChild(grid);
            });
        } else {
            const grid = document.createElement("div");
            grid.className = "grid-container";

            // Sort stories roughly numerically within a type
            let sortedGroupIds = typeMap[type].sort((a, b) => parseInt(a) - parseInt(b));
            renderCardsToGrid(sortedGroupIds, grid);
            section.appendChild(grid);
        }

        sectionsContainer.appendChild(section);
    });
}

function renderCardsToGrid(groupIds, grid) {
    groupIds.forEach(g_id => {
        const data = groupsData[g_id];
        // Get title for current region, fallback to any available if missing
        let title = data.titles[currentRegion];
        if (!title) {
            const available = Object.keys(data.titles);
            if (available.length > 0) title = data.titles[available[0]] + ` (${available[0]})`;
            else title = `Group ${g_id}`;
        }

        const card = document.createElement("a");
        card.className = "card";
        card.href = `story.html?id=${g_id}`;

        card.innerHTML = `
            <div class="card-img-placeholder">
                Story Group ${g_id} <br>
                Type-SubType: ${data.type}-${data.subtype}<br>
                Icon: ${data.icon}<br>
            </div>
            <div class="card-title">${title}</div>
        `;
        grid.appendChild(card);
    });
}

// Start app
fetchGroupsData();
