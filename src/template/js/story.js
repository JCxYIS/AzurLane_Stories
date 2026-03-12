let storyData = {};
let titlesData = {};

const regionTabsContainer = document.getElementById('region-tabs');
const chapterTabsContainer = document.getElementById('chapter-tabs');
const contentContainer = document.getElementById('story-content');
const titleElem = document.getElementById('story-title');

let currentRegion = null;
let currentChapter = null;
const regionOrder = ["EN", "CN", "JP", "KR", "TW"];
let availableRegions = [];

async function fetchStoryData() {
  try {
    const urlParams = new URLSearchParams(window.location.search);
    const groupId = urlParams.get('id');

    if (!groupId) {
      titleElem.textContent = "Error: No story ID provided";
      return;
    }

    const response = await fetch(`stories/${groupId}/data.json`);
    const data = await response.json();

    storyData = data.regions;
    titlesData = data.titles;

    availableRegions = Object.keys(storyData).sort((a, b) => {
      let ia = regionOrder.indexOf(a), ib = regionOrder.indexOf(b);
      if (ia === -1) ia = 99; if (ib === -1) ib = 99;
      return ia - ib;
    });

    init();
  } catch (e) {
    console.error("Failed to load story data", e);
    titleElem.textContent = "Error loading story data.";
    contentContainer.innerHTML = "<p>Ensure you are running a local web server (e.g., python -m http.server).</p>";
  }
}

function init() {
  if (availableRegions.length === 0) return;

  const savedRegion = localStorage.getItem('selectedRegion');
  if (savedRegion && availableRegions.includes(savedRegion)) {
    currentRegion = savedRegion;
  } else {
    // Default to EN or JP if possible
    currentRegion = availableRegions[0];
    if (availableRegions.includes("EN")) currentRegion = "EN";
    else if (availableRegions.includes("JP")) currentRegion = "JP";
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

  if (titleElem && titlesData[region]) {
    titleElem.textContent = titlesData[region];
    document.title = "Story: " + titlesData[region];
  }

  Array.from(regionTabsContainer.children).forEach(btn => {
    btn.classList.toggle('active', btn.textContent === region);
  });

  renderChapterTabs();

  const chapters = Object.keys(storyData[region]);
  if (!chapters.includes(currentChapter)) {
    currentChapter = chapters[0];
  }
  selectChapter(currentChapter);
}

function renderChapterTabs() {
  chapterTabsContainer.innerHTML = '';
  if (!storyData[currentRegion]) return;

  const chapters = Object.keys(storyData[currentRegion]);

  chapters.forEach(chapter => {
    const btn = document.createElement('button');
    btn.className = 'chapter-btn';
    btn.textContent = chapter;
    btn.onclick = () => selectChapter(chapter);
    if (chapter === currentChapter) btn.classList.add('active');
    chapterTabsContainer.appendChild(btn);
  });
}

function selectChapter(chapter) {
  currentChapter = chapter;

  Array.from(chapterTabsContainer.children).forEach(btn => {
    btn.classList.toggle('active', btn.textContent === chapter);
  });

  renderContent();
}

function renderContent() {
  contentContainer.innerHTML = '';
  const scripts = storyData[currentRegion][currentChapter];
  if (!scripts) return;

  scripts.forEach(s => {
    if (s.stopbgm) {
      const div = document.createElement('div');
      div.className = 'bgm-change';
      div.innerHTML = '⏸ BGM Stopped';
      contentContainer.appendChild(div);
    }
    if (s.bgm) {
      const div = document.createElement('div');
      div.className = 'bgm-change';
      div.innerHTML = '▶ BGM: ' + s.bgm;
      contentContainer.appendChild(div);
    }
    if (s.bgName) {
      const div = document.createElement('div');
      div.className = 'bg-change';
      div.innerHTML = '🖼 Background: ' + s.bgName;
      contentContainer.appendChild(div);
    }
    if (s.sequence) {
      const div = document.createElement('div');
      div.className = 'sequence';
      s.sequence.forEach(line => {
        const p = document.createElement('div');
        p.innerHTML = line;
        div.appendChild(p);
      });
      contentContainer.appendChild(div);
    }

    if (s.say) {
      if (s.narration) {
        const div = document.createElement('div');
        div.className = 'narration';
        div.innerHTML = s.say;
        contentContainer.appendChild(div);
      } else {
        const box = document.createElement('div');
        box.className = 'dialogue-box';

        const bannerDiv = document.createElement('div');
        bannerDiv.className = 'actor-banner';
        if (s.actor) {
          const img = document.createElement('img');
          img.src = `https://raw.githubusercontent.com/Fernando2603/AzurLane/main/images/skin/${s.actor}/banner.png`;
          img.alt = `${s.actorName} (${s.actor})`;
          // img.onerror = () => { img.style.display = 'none'; }; // Graceful fallback
          bannerDiv.appendChild(img);
        }

        const contentDiv = document.createElement('div');
        contentDiv.className = 'dialogue-content';

        const nameDiv = document.createElement('div');
        nameDiv.className = 'actor-name';
        if (s.nameColor) {
          nameDiv.style.color = s.nameColor;
        }
        nameDiv.innerHTML = s.actorName;
        if (s.factiontag) {
          nameDiv.innerHTML += "<span class='factiontag'>" + s.factiontag + "</span>";
        }

        // const factiontagDiv = document.createElement('div');
        // factiontagDiv.className = 'factiontag';
        // if (s.factiontag) {
        //   factiontagDiv.innerHTML = s.factiontag;
        // }

        const textDiv = document.createElement('div');
        textDiv.innerHTML = s.say;

        contentDiv.appendChild(nameDiv);
        contentDiv.appendChild(textDiv);

        box.appendChild(bannerDiv);
        box.appendChild(contentDiv);
        contentContainer.appendChild(box);
      }
    }
  });
}

fetchStoryData();
