const STORAGE_KEY = "tcm-constitution-answers-v2";
const RESULT_LOCK_KEY = "tcm-constitution-result-lock-v2";
const GENDER_KEY = "tcm-constitution-gender-v1";

const types = {
  PH: {
    label: "平和质",
    code: "PH",
    color: "#2f6b4f",
    archetype: "衡庭使者",
    tagline: "把节律、关系和能量都维持在稳定中轴。",
    images: {
      female: "assets/characters/female/ph.webp",
      male: "assets/characters/male/ph.webp",
    },
    short: "整体协调，适应力较好。",
    description:
      "平和质通常表现为精力、睡眠、消化和情绪相对稳定，是九种体质中较为均衡的状态。",
    advice: {
      起居: "保持规律作息和适度运动，避免长期熬夜、过度节食或突然增加高强度训练。",
      饮食: "维持多样、清淡、有节制的饮食结构，少让辛辣油腻和冰冷饮品成为日常。",
      情志: "继续保留能让你恢复精力的稳定节奏，定期观察身体变化即可。",
    },
  },
  QX: {
    label: "气虚质",
    code: "QX",
    color: "#3f7d91",
    archetype: "补给灯塔守",
    tagline: "能量像灯塔油仓，需要稳定补给才会持续发亮。",
    images: {
      female: "assets/characters/female/qx.webp",
      male: "assets/characters/male/qx.webp",
    },
    short: "容易疲乏，耐力和防御力偏弱。",
    description:
      "气虚质常见疲倦、气短、易汗、声音低弱等表现，身体恢复速度可能慢一些。",
    advice: {
      起居: "把睡眠和午间短休放在优先级更高的位置，运动以散步、八段锦、轻力量为主。",
      饮食: "偏向温和、易消化的三餐，留意蛋白质和主食摄入，不建议长期空腹或过度生冷。",
      情志: "减少连续透支型安排，把任务切成短段完成，给恢复留出确定时间。",
    },
  },
  YA: {
    label: "阳虚质",
    code: "YA",
    color: "#b4852d",
    archetype: "日炉守护者",
    tagline: "随身带着小太阳，先把身体的火候稳住。",
    images: {
      female: "assets/characters/female/ya.webp",
      male: "assets/characters/male/ya.webp",
    },
    short: "偏怕冷，温煦能力不足。",
    description:
      "阳虚质常见手脚冷、怕冷、喜热饮、腹部或腰膝发冷等表现，身体对寒凉更敏感。",
    advice: {
      起居: "注意颈肩、腰腹、足部保暖，避免久坐寒湿环境，运动选择能稳定升温的低中强度项目。",
      饮食: "少吃冰饮、生冷和过量寒凉水果，三餐尽量温热、规律、不过饥过饱。",
      情志: "把早睡和晨间日光暴露固定下来，减少长期夜间工作带来的阳气消耗。",
    },
  },
  YN: {
    label: "阴虚质",
    code: "YN",
    color: "#b44b35",
    archetype: "月井观测者",
    tagline: "在燥热里寻找清泉，学会给自己降噪与补水。",
    images: {
      female: "assets/characters/female/yn.webp",
      male: "assets/characters/male/yn.webp",
    },
    short: "偏干偏热，安静恢复不足。",
    description:
      "阴虚质常见口干、手足心热、睡眠浅、盗汗、大便偏干等表现，身体像缺少润泽和缓冲。",
    advice: {
      起居: "减少熬夜和高压连续输出，运动避免长期过热大汗，重视睡前降噪和放松。",
      饮食: "少用辛辣、烧烤、烈酒和过度温燥食物，增加水分充足、质地柔润的日常饮食。",
      情志: "给脑力工作设置停止线，避免用咖啡因和刺激性内容硬撑疲劳。",
    },
  },
  TS: {
    label: "痰湿质",
    code: "TS",
    color: "#6b7d4b",
    archetype: "雾沼搬运师",
    tagline: "把沉重和黏滞一点点搬开，让身体重新流动。",
    images: {
      female: "assets/characters/female/ts.webp",
      male: "assets/characters/male/ts.webp",
    },
    short: "沉重黏滞，代谢负担感明显。",
    description:
      "痰湿质常见身体沉重、腹部肥满、皮肤油腻、痰多、饭后困倦等表现。",
    advice: {
      起居: "增加低冲击有氧和日常步数，避免久坐后直接大量进食，保持居住环境干爽通风。",
      饮食: "控制甜食、油炸、夜宵和过量奶茶酒饮，三餐更重视蔬菜、优质蛋白和饱腹但不腻的结构。",
      情志: "用固定运动和固定用餐时间打破拖延循环，别把困倦简单归因于意志力不足。",
    },
  },
  SR: {
    label: "湿热质",
    code: "SR",
    color: "#8b5a2b",
    archetype: "雨巷清障官",
    tagline: "穿过闷热和黏腻，给身体开一条清爽通道。",
    images: {
      female: "assets/characters/female/sr.webp",
      male: "assets/characters/male/sr.webp",
    },
    short: "油热夹湿，清爽感不足。",
    description:
      "湿热质常见面部油光、痘痘、口苦口臭、小便偏黄、大便黏滞等表现。",
    advice: {
      起居: "保证出汗后的清洁和干爽，避免长期闷热环境，运动以能持续但不过度爆发的方式为宜。",
      饮食: "减少辛辣、油炸、酒精、重口味和高糖饮品，留意晚餐过饱与皮肤、口气、睡眠的关系。",
      情志: "急躁和压力会放大湿热感，给高强度工作之间安排短暂降温和离屏时间。",
    },
  },
  XY: {
    label: "血瘀质",
    code: "XY",
    color: "#6e4b7e",
    archetype: "赤脉修复师",
    tagline: "把停滞的脉络重新点亮，减少暗滞和固定疼痛。",
    images: {
      female: "assets/characters/female/xy.webp",
      male: "assets/characters/male/xy.webp",
    },
    short: "循环不畅，暗滞和固定痛更突出。",
    description:
      "血瘀质常见肤色晦暗、唇色偏暗、固定刺痛、眼下暗、易有瘀斑等表现。",
    advice: {
      起居: "避免久坐不动和长期受寒，选择规律步行、拉伸、轻力量来改善身体活动度。",
      饮食: "少让高脂厚味成为常态，保持饮水、蔬果和优质蛋白，酒精不应作为促进循环的手段。",
      情志: "把压力和睡眠纳入观察，长期疼痛、胸闷或异常出血应及时就医。",
    },
  },
  QY: {
    label: "气郁质",
    code: "QY",
    color: "#315f8c",
    archetype: "风结解语者",
    tagline: "把胸口的结慢慢解开，让气机重新有出口。",
    images: {
      female: "assets/characters/female/qy.webp",
      male: "assets/characters/male/qy.webp",
    },
    short: "情绪郁滞，胸胁不舒。",
    description:
      "气郁质常见情绪低落、胸胁胀满、易叹气、咽中异物感、睡眠多梦等表现。",
    advice: {
      起居: "每天安排可完成的户外活动或伸展，减少长时间独处久坐和无边界的信息摄入。",
      饮食: "规律进食，少用暴食、酒精或高糖来处理压力，晚餐避免过晚过饱。",
      情志: "优先处理压力源和沟通边界；若低落、焦虑或失眠持续影响生活，应寻求专业帮助。",
    },
  },
  TB: {
    label: "特禀质",
    code: "TB",
    color: "#7b5f45",
    archetype: "边界侦测员",
    tagline: "对环境变化高度敏感，擅长发现别人忽略的触发点。",
    images: {
      female: "assets/characters/female/tb.webp",
      male: "assets/characters/male/tb.webp",
    },
    short: "敏感体质，过敏或反应性更强。",
    description:
      "特禀质常见鼻炎、皮肤风团、对尘螨花粉食物敏感、喘鸣或皮肤划痕明显等表现。",
    advice: {
      起居: "记录并规避明确诱因，关注空气质量、寝具清洁和季节变化，运动时留意呼吸反应。",
      饮食: "对已知过敏食物保持严格边界，不建议盲目尝试偏方或大范围忌口。",
      情志: "建立过敏发作记录，严重喘憋、喉头紧缩或全身反应需要立即就医。",
    },
  },
};

const questions = [
  ["PH", "你大多数日子精力比较充足，完成日常事务后仍有余力。"],
  ["QX", "你容易感到疲倦，即使休息后恢复也比较慢。"],
  ["YA", "你比身边人更怕冷，手脚或腹部常常发凉。"],
  ["YN", "你经常口干、咽干，或总想少量多次喝水。"],
  ["TS", "你常觉得身体沉重、困倦，像被拖住一样。"],
  ["SR", "你容易面部油光、长痘，或皮肤有湿热瘙痒感。"],
  ["XY", "你的肤色、唇色或眼下容易显得偏暗。"],
  ["QY", "你容易情绪低落、烦闷，或常有说不出的压力感。"],
  ["TB", "你有过敏性鼻炎、荨麻疹、哮喘或明显过敏史。"],
  ["PH", "你的胃口、消化和排便大多稳定，很少被饮食轻易扰乱。"],
  ["QX", "你说话声音偏低，或不太想多说话。"],
  ["YA", "你喜欢热饮热食，吃冷饮或受凉后容易不舒服。"],
  ["YN", "你容易手心、脚心发热，或午后脸颊发热。"],
  ["TS", "你腹部容易肥满，体重或围度管理比较吃力。"],
  ["SR", "你容易口苦、口黏、口气重。"],
  ["XY", "你身体某些部位会有固定位置的刺痛或胀痛。"],
  ["QY", "你紧张或郁闷时容易胸胁胀、胃口变差。"],
  ["TB", "你对花粉、尘螨、宠物毛发或季节变化很敏感。"],
  ["PH", "你的睡眠质量大多稳定，醒后精神还不错。"],
  ["QX", "你稍微活动后就容易气短、心慌或需要停下来。"],
  ["YA", "你腰、膝、腹部或背部容易有冷感。"],
  ["YN", "你睡眠偏浅，或夜间容易出汗、醒来觉得热。"],
  ["TS", "你皮肤或头发容易油腻，或喉咙里常有痰感。"],
  ["SR", "你小便颜色经常偏黄，或大便黏滞不爽。"],
  ["XY", "你容易出现瘀斑、色斑，或局部青筋明显。"],
  ["QY", "你常常不自觉叹气，叹完会舒服一点。"],
  ["TB", "你吃到某些食物、接触某些环境后容易皮肤红痒或起疹。"],
  ["PH", "你情绪总体平稳，遇到变化也比较容易调整回来。"],
  ["QX", "你比别人更容易出汗，尤其是轻微活动或紧张时。"],
  ["YA", "你大便容易偏稀，或夜尿、清长小便较明显。"],
  ["YN", "你大便容易偏干，或皮肤、眼睛容易干涩。"],
  ["TS", "你饭后特别容易犯困，或甜腻油重后更明显。"],
  ["SR", "你在闷热、熬夜或重口味饮食后更容易烦躁上火。"],
  ["XY", "你的舌下、唇色或指甲颜色有时偏暗紫。"],
  ["QY", "你会有咽中像堵着东西、想清嗓但不一定有痰的感觉。"],
  ["TB", "你的皮肤被抓挠后容易出现明显红痕或风团。"],
  ["PH", "你不太容易反复感冒，季节变化时适应力还不错。"],
  ["QX", "你容易反复感冒，或换季时抵抗力明显下降。"],
  ["YA", "你在阴雨、空调房或寒冷天气里状态明显变差。"],
  ["YN", "你在熬夜、辛辣或压力大后更容易出现燥热不适。"],
  ["TS", "你不喜欢潮湿天气，潮湿时身体沉重或困乏更明显。"],
  ["SR", "你容易出现湿疹、痘痘、私处潮湿或分泌物偏黄等困扰。"],
  ["XY", "你久坐、受寒或压力大后，身体僵硬和疼痛更明显。"],
  ["QY", "你入睡困难、多梦，或醒来后仍觉得心里不松快。"],
  ["TB", "你曾因过敏、喘憋或皮肤反应需要用药或就医。"],
].map(([type, text], index) => ({ id: index + 1, type, text }));

const scale = [
  { value: 1, label: "从不", detail: "几乎不符合" },
  { value: 2, label: "很少", detail: "偶尔一点" },
  { value: 3, label: "有时", detail: "说不准" },
  { value: 4, label: "经常", detail: "比较符合" },
  { value: 5, label: "总是", detail: "非常符合" },
];

let answers = loadAnswers();
let currentIndex = firstUnansweredIndex();
let lockedResult = loadLockedResult();
let selectedGender = loadGender();

const els = {
  answeredCount: document.getElementById("answeredCount"),
  progressFill: document.getElementById("progressFill"),
  sidebarNote: document.getElementById("sidebarNote"),
  constitutionMap: document.getElementById("constitutionMap"),
  questionNumber: document.getElementById("questionNumber"),
  questionText: document.getElementById("questionText"),
  questionHint: document.getElementById("questionHint"),
  genderOptions: document.getElementById("genderOptions"),
  scaleOptions: document.getElementById("scaleOptions"),
  prevBtn: document.getElementById("prevBtn"),
  nextBtn: document.getElementById("nextBtn"),
  resetBtn: document.getElementById("resetBtn"),
  testPanel: document.getElementById("testPanel"),
  resultPanel: document.getElementById("resultPanel"),
  resultTitle: document.getElementById("resultTitle"),
  resultSummary: document.getElementById("resultSummary"),
  resultCode: document.getElementById("resultCode"),
  primaryCharacterImage: document.getElementById("primaryCharacterImage"),
  primaryArchetype: document.getElementById("primaryArchetype"),
  primaryLabel: document.getElementById("primaryLabel"),
  primaryDescription: document.getElementById("primaryDescription"),
  scoreList: document.getElementById("scoreList"),
  adviceGrid: document.getElementById("adviceGrid"),
  copyBtn: document.getElementById("copyBtn"),
  toast: document.getElementById("toast"),
};

function loadAnswers() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    return typeof saved === "object" && saved ? saved : {};
  } catch {
    return {};
  }
}

function loadLockedResult() {
  try {
    const saved = JSON.parse(localStorage.getItem(RESULT_LOCK_KEY) || "null");
    return saved && typeof saved === "object" ? saved : null;
  } catch {
    return null;
  }
}

function loadGender() {
  const saved = localStorage.getItem(GENDER_KEY);
  return saved === "male" ? "male" : "female";
}

function saveAnswers() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(answers));
}

function saveLockedResult(payload) {
  lockedResult = payload;
  localStorage.setItem(RESULT_LOCK_KEY, JSON.stringify(payload));
}

function saveGender() {
  localStorage.setItem(GENDER_KEY, selectedGender);
}

function firstUnansweredIndex() {
  const index = questions.findIndex((question) => !answers[question.id]);
  return index === -1 ? questions.length - 1 : index;
}

function answeredTotal() {
  return questions.filter((question) => answers[question.id]).length;
}

function renderMap(scores = null) {
  els.constitutionMap.classList.toggle("locked", !scores);

  if (!scores) {
    els.sidebarNote.textContent =
      "角色档案将在完成测试后解锁。答题阶段不会显示题目对应的体质维度。";
    els.constitutionMap.innerHTML = Array.from({ length: 9 }, (_, index) => {
      return `
        <div class="type-chip mystery">
          <span>角色 ${String(index + 1).padStart(2, "0")}</span>
          <strong>待解锁</strong>
        </div>
      `;
    }).join("");
    return;
  }

  els.sidebarNote.textContent = "九个角色档案已解锁，分数越高代表该体质线索越明显。";
  els.constitutionMap.innerHTML = Object.values(types)
    .map((type) => {
      const score = scores[type.code].normalized;
      return `
        <div class="type-chip unlocked">
          <img src="${imageFor(type)}" alt="${type.archetype}" loading="lazy" />
          <span>${type.code} ${score}分</span>
          <strong>${type.archetype}</strong>
          <em>${type.label}</em>
        </div>
      `;
    })
    .join("");
}

function imageFor(type, gender = selectedGender) {
  const inline =
    window.TCM_ASSETS?.characters?.[gender]?.[type.code] ||
    window.TCM_ASSETS?.characters?.[gender]?.[type.code.toLowerCase()];
  return inline || type.images?.[gender] || type.images?.female || "";
}

function renderGenderOptions() {
  els.genderOptions.querySelectorAll("button").forEach((button) => {
    const active = button.dataset.gender === selectedGender;
    button.setAttribute("aria-pressed", String(active));
  });
}

function renderHeroImage() {
  const hero = document.getElementById("heroImage");
  if (hero && window.TCM_ASSETS?.hero) {
    hero.src = window.TCM_ASSETS.hero;
  }
}

function renderProgress() {
  const count = answeredTotal();
  els.answeredCount.textContent = count;
  els.progressFill.style.width = `${Math.round((count / questions.length) * 100)}%`;
}

function renderQuestion() {
  const question = questions[currentIndex];
  els.questionNumber.textContent = `第 ${currentIndex + 1} 题 / ${questions.length}`;
  els.questionText.textContent = question.text;
  els.questionHint.textContent =
    "请按最近 3 个月的整体状态作答，不要只按某一天的情绪或临时不适判断。";
  els.prevBtn.disabled = currentIndex === 0;
  els.nextBtn.textContent =
    answeredTotal() === questions.length && currentIndex === questions.length - 1
      ? "查看结果"
      : "下一题";

  els.scaleOptions.innerHTML = scale
    .map((option) => {
      const checked = answers[question.id] === option.value;
      return `
        <button class="scale-option" type="button" role="radio" aria-checked="${checked}" data-value="${option.value}">
          <strong>${option.label}</strong>
          <span>${option.detail}</span>
        </button>
      `;
    })
    .join("");
}

function setAnswer(value) {
  if (lockedResult) {
    showToast("结果已锁定，请重新开始新的测试");
    return;
  }

  const question = questions[currentIndex];
  answers[question.id] = value;
  saveAnswers();
  renderProgress();
  renderQuestion();

  if (currentIndex < questions.length - 1) {
    window.setTimeout(() => {
      currentIndex += 1;
      renderQuestion();
    }, 120);
  } else if (answeredTotal() === questions.length) {
    window.setTimeout(finalizeResult, 160);
  }
}

function calculateScores(sourceAnswers = answers) {
  const scores = Object.fromEntries(
    Object.keys(types).map((code) => [code, { raw: 0, count: 0, normalized: 0 }]),
  );

  questions.forEach((question) => {
    scores[question.type].raw += sourceAnswers[question.id] || 0;
    scores[question.type].count += 1;
  });

  Object.values(scores).forEach((score) => {
    const min = score.count;
    const max = score.count * 5;
    score.normalized = Math.round(((score.raw - min) / (max - min)) * 100);
  });

  return scores;
}

function classify(scores) {
  const entries = Object.keys(types).map((code) => ({
    code,
    ...types[code],
    score: scores[code].normalized,
  }));
  const balanced = entries.find((entry) => entry.code === "PH");
  const imbalanced = entries
    .filter((entry) => entry.code !== "PH")
    .sort((a, b) => b.score - a.score);
  const top = imbalanced[0];

  if (balanced.score >= 70 && top.score < 45) {
    return {
      kind: "balanced",
      primary: balanced,
      selected: [balanced],
      code: "PH",
      title: `${balanced.archetype} · ${balanced.label}`,
      summary:
        "你的整体状态更接近平和质。当前最重要的是保持稳定节奏，避免长期透支把均衡状态拉偏。",
    };
  }

  const selected = imbalanced
    .filter((entry) => entry.score >= 55 || top.score - entry.score <= 8)
    .slice(0, 3);
  const primary = selected[0];
  const tendencyText = top.score < 65 ? "倾向" : "主导";
  const title =
    selected.length > 1
      ? `${selected.map((entry) => entry.archetype).join(" + ")}复合${tendencyText}`
      : `${primary.archetype} · ${primary.label}${tendencyText}`;

  return {
    kind: selected.length > 1 ? "composite" : "single",
    primary,
    selected,
    code: selected.map((entry) => entry.code).join("-"),
    title,
    summary:
      selected.length > 1
        ? "你的结果呈现复合特征。建议先处理分数最高的体质线索，再观察第二、第三体质是否随作息、饮食和压力变化而下降。"
        : "你的结果以单一体质线索为主。建议先围绕该体质的高频表现做 2 到 4 周的生活方式调整，再复测观察变化。",
  };
}

function buildResultPayload() {
  const scores = calculateScores();
  const result = classify(scores);
  return {
    createdAt: new Date().toISOString(),
    gender: selectedGender,
    answers: { ...answers },
    scores,
    result: {
      code: result.code,
      title: result.title,
      summary: result.summary,
      primaryCode: result.primary.code,
      selectedCodes: result.selected.map((entry) => entry.code),
    },
  };
}

function finalizeResult() {
  if (answeredTotal() < questions.length) {
    showToast("还有题目未完成");
    return;
  }

  const payload = lockedResult || buildResultPayload();
  saveLockedResult(payload);
  showResult(payload);
}

function showResult(payload = lockedResult) {
  if (!payload) return;

  const scores = payload.scores;
  const resultGender = payload.gender === "male" ? "male" : "female";
  const selected = payload.result.selectedCodes.map((code) => ({
    ...types[code],
    score: scores[code].normalized,
  }));
  const primary = { ...types[payload.result.primaryCode], score: scores[payload.result.primaryCode].normalized };
  const sortedScores = Object.values(types)
    .map((type) => ({ ...type, score: scores[type.code].normalized }))
    .sort((a, b) => b.score - a.score);

  els.testPanel.classList.add("hidden");
  els.resultPanel.classList.remove("hidden");
  renderMap(scores);
  renderProgress();

  els.resultTitle.textContent = payload.result.title;
  els.resultSummary.textContent = payload.result.summary;
  els.resultCode.textContent = payload.result.code;
  els.primaryCharacterImage.src = imageFor(primary, resultGender);
  els.primaryCharacterImage.alt = primary.archetype;
  els.primaryArchetype.textContent = `${primary.archetype}｜${primary.tagline}`;
  els.primaryLabel.textContent = primary.label;
  els.primaryDescription.textContent = primary.description;

  els.scoreList.innerHTML = sortedScores
    .map(
      (entry) => `
        <div class="score-row">
          <div class="score-name">
            <strong>${entry.archetype}</strong>
            <span>${entry.label}</span>
          </div>
          <div class="bar-track">
            <div class="bar-fill" style="width:${entry.score}%; background:${entry.color}"></div>
          </div>
          <div class="score-value">${entry.score}</div>
        </div>
      `,
    )
    .join("");

  els.adviceGrid.innerHTML = selected
    .flatMap((entry) =>
      Object.entries(entry.advice).map(
        ([title, body]) => `
          <article class="advice-block">
            <h4>${entry.archetype} · ${title}</h4>
            <p>${body}</p>
          </article>
        `,
      ),
    )
    .slice(0, 6)
    .join("");

  window.scrollTo({ top: 0, behavior: "smooth" });
}

function resetTest() {
  answers = {};
  lockedResult = null;
  currentIndex = 0;
  localStorage.removeItem(STORAGE_KEY);
  localStorage.removeItem(RESULT_LOCK_KEY);
  saveGender();
  renderMap();
  renderProgress();
  els.resultPanel.classList.add("hidden");
  els.testPanel.classList.remove("hidden");
  renderQuestion();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function resultText() {
  const payload = lockedResult || buildResultPayload();
  const scoreText = Object.values(types)
    .map((type) => `${type.archetype}/${type.label}${payload.scores[type.code].normalized}分`)
    .join("、");
  return `九型中医体质人格测试结果：${payload.result.title}（${payload.result.code}）。${payload.result.summary} 各项分数：${scoreText}。本测试仅用于自我观察，不构成医疗诊断。`;
}

async function copyResult() {
  const text = resultText();
  try {
    await navigator.clipboard.writeText(text);
    showToast("结果摘要已复制");
  } catch {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
    showToast("结果摘要已复制");
  }
}

function showToast(message) {
  els.toast.textContent = message;
  els.toast.classList.add("show");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    els.toast.classList.remove("show");
  }, 1800);
}

els.scaleOptions.addEventListener("click", (event) => {
  const button = event.target.closest(".scale-option");
  if (!button) return;
  setAnswer(Number(button.dataset.value));
});

els.prevBtn.addEventListener("click", () => {
  if (lockedResult) {
    showToast("结果已锁定，请重新开始新的测试");
    return;
  }
  currentIndex = Math.max(0, currentIndex - 1);
  renderQuestion();
});

els.nextBtn.addEventListener("click", () => {
  if (lockedResult) {
    showToast("结果已锁定，请重新开始新的测试");
    return;
  }

  if (!answers[questions[currentIndex].id]) {
    showToast("请选择一个符合程度");
    return;
  }

  if (currentIndex === questions.length - 1) {
    finalizeResult();
    return;
  }

  currentIndex += 1;
  renderQuestion();
});

els.resetBtn.addEventListener("click", resetTest);
els.copyBtn.addEventListener("click", copyResult);
els.genderOptions.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-gender]");
  if (!button) return;

  if (lockedResult) {
    showToast("结果已锁定，请重新开始新的测试");
    return;
  }

  selectedGender = button.dataset.gender === "male" ? "male" : "female";
  saveGender();
  renderGenderOptions();
});

renderHeroImage();
if (lockedResult) {
  answers = { ...lockedResult.answers };
  selectedGender = lockedResult.gender === "male" ? "male" : "female";
  renderGenderOptions();
  showResult(lockedResult);
} else {
  renderGenderOptions();
  renderMap();
  renderProgress();
  renderQuestion();
}
