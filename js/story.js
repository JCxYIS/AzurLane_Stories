let storyData = {};
let titlesData = {};

let showDebugInfo = false;
let hideUi = false;

const regionTabsContainer = document.getElementById('region-tabs');
const chapterTabsContainer = document.getElementById('chapter-tabs');
const contentContainer = document.getElementById('story-content');
const titleElem = document.getElementById('story-title');

let currentRegion = null;
let currentChapter = null;
const regionOrder = ["EN", "CN", "JP", "KR", "TW"];
let availableRegions = [];

const bgmPlayer = new Audio();
bgmPlayer.loop = true;

const musicPlayBtn = document.getElementById('music-play-btn');
const musicVolume = document.getElementById('music-volume');
const musicSongId = document.getElementById('music-song-id');

// Load saved volume
const savedVolume = localStorage.getItem('bgmVolume');
if (savedVolume !== null) {
  bgmPlayer.volume = parseFloat(savedVolume);
  musicVolume.value = savedVolume;
}

musicPlayBtn.onclick = () => {
  if (bgmPlayer.paused) {
    if (bgmPlayer.src) {
      bgmPlayer.play();
    } else {
      // bgmPlayer.src = 'https://cdn.nagami.moe/bgm/bgm-main.ogg';
      bgmPlayer.src = 'https://raw.githubusercontent.com/Fernando2603/AzurLane/main/audio/bgm/main.ogg';
      bgmPlayer.play().catch(e => console.error("Audio playback failed", e));
    }
  } else {
    bgmPlayer.pause();
  }
  updateMusicUI();
};

musicVolume.oninput = () => {
  bgmPlayer.volume = musicVolume.value;
  localStorage.setItem('bgmVolume', musicVolume.value);
};

function updateMusicUI() {
  musicPlayBtn.textContent = bgmPlayer.paused ? '▶' : '⏸';
  if (bgmPlayer.src) {
    const url = new URL(bgmPlayer.src);
    const filename = url.pathname.split('/').pop();
    const songId = filename.replace('bgm-', '').replace('.ogg', '');
    musicSongId.textContent = songId;
  } else {
    musicSongId.textContent = 'No BGM';
  }
}

bgmPlayer.onplay = updateMusicUI;
bgmPlayer.onpause = updateMusicUI;

// if we came from the index page, go back to preserve its state (scroll, tabs)
const backLink = document.querySelector('.back-link');
if (backLink) {
  backLink.onclick = (e) => {
    if (document.referrer && document.referrer.includes('index.html')) {
      console.log("Referer is index.html, use go back instead of redirect.");
      e.preventDefault();
      window.history.back();
    }
  };
}

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
    contentContainer.innerHTML = `
    <img src="https://raw.githubusercontent.com/Fernando2603/AzurLane/main/images/skin/305055/painting.png" style="width: 100%;">
    <p style="text-align: center;">Looks like you walk into a wrong door... Only our cute Nagato-sama stranded here.</p>
    `;
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
    else if (availableRegions.includes("CN")) currentRegion = "CN";
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
  // lookup new chapter name in new language
  const chapters = Object.keys(storyData[currentRegion]);
  let newChapterIndex = 0;
  if (chapters.includes(currentChapter)) {
    newChapterIndex = chapters.indexOf(currentChapter);
  }
  const chaptersNewRegion = Object.keys(storyData[region])
  currentChapter = chaptersNewRegion[newChapterIndex];

  currentRegion = region;
  localStorage.setItem('selectedRegion', region);

  if (titleElem && titlesData[region]) {
    titleElem.textContent = titlesData[region];
    document.title = "AZL Story: " + titlesData[region];
  }

  Array.from(regionTabsContainer.children).forEach(btn => {
    btn.classList.toggle('active', btn.textContent === region);
  });

  renderChapterTabs();
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
  document.body.style.backgroundImage = "";

  Array.from(chapterTabsContainer.children).forEach(btn => {
    btn.classList.toggle('active', btn.textContent === chapter);
  });

  renderContent();

  window.scrollTo({
    top: 1,
    behavior: 'smooth'
  });
}

function renderContent() {
  contentContainer.innerHTML = '';
  const scripts = storyData[currentRegion][currentChapter];
  if (!scripts) return;

  let activeOptions = [];
  let renderedOptionFlags = new Set();
  let insideOptionBranch = false;

  scripts.forEach((s, index) => {
    if (s.options && s.options.length > 0) {
      activeOptions = s.options;
      renderedOptionFlags.clear();
      insideOptionBranch = false;
    }

    if (s.optionFlag !== undefined) {
      if (!renderedOptionFlags.has(s.optionFlag)) {
        renderedOptionFlags.add(s.optionFlag);
        insideOptionBranch = true;

        const hr = document.createElement('hr');
        contentContainer.appendChild(hr);

        // const optIndex = activeOptions.findIndex(o => o.flag === s.optionFlag) + 1;
        const optContent = activeOptions.find(o => o.flag === s.optionFlag)?.content || '';

        const optDiv = document.createElement('div');
        optDiv.className = 'option-title';
        optDiv.innerHTML = `<strong>&gt; ${optContent}</strong>`;
        contentContainer.appendChild(optDiv);
      }
    } else {
      if (insideOptionBranch) {
        insideOptionBranch = false;
        const hr = document.createElement('hr');
        contentContainer.appendChild(hr);
      }
    }
    // stop bgm is typically top-priority (to stop last playback)
    if (s.stopbgm) {
      const div = document.createElement('div');
      div.className = 'bgm-change';
      div.innerHTML = '⏸ BGM Stopped';
      div.onclick = () => {
        bgmPlayer.pause();
      };
      contentContainer.appendChild(div);
    }
    if (s.bgm) {
      const div = document.createElement('div');
      div.className = 'bgm-change';
      div.innerHTML = '▶ BGM: ' + s.bgm;
      div.onclick = () => {
        // const src = `https://cdn.nagami.moe/bgm/bgm-${s.bgm}.ogg`;
        const src = `https://raw.githubusercontent.com/Fernando2603/AzurLane/main/audio/bgm/${s.bgm}.ogg`;
        if (src !== bgmPlayer.src) {
          bgmPlayer.src = src;
        }
        bgmPlayer.play().catch(e => alert("Audio playback failed", e));
      };
      contentContainer.appendChild(div);
    }
    if (s.bgName) {
      const div = document.createElement('div');
      div.className = 'bg-change';
      div.innerHTML = '🖼 Background: ' + s.bgName;
      div.style.cursor = 'pointer';
      let urlStr = `url(https://cdn.nagami.moe/bg/${s.bgName}.png)`;
      if (!document.body.style.backgroundImage) {
        document.body.style.backgroundImage = urlStr;
      }
      div.onclick = () => {
        document.body.style.backgroundImage = urlStr;
      };
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
        else {
          // hide banner if no actor
          // bannerDiv.style.display = 'none';
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


// Toggle debug info with 'i' key
document.addEventListener('keydown', (e) => {
  if (e.key.toLowerCase() === 'i') {
    showDebugInfo = !showDebugInfo;
  }
  if (e.key.toLowerCase() === 'o') {
    hideUi = !hideUi;
    document.body.style.opacity = hideUi ? 0 : 1;
    document.body.style.transition = 'opacity 0.25s';
  }
});
