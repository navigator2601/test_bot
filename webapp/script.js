// Ініціалізація Telegram WebApp
const tg = window.Telegram ? window.Telegram.WebApp : null;

if (tg) {
  tg.expand(); // на весь екран

  // Підставляємо юзера в статус, якщо є
  const user = tg.initDataUnsafe?.user;
  if (user) {
    const statusText = document.getElementById("status-text");
    statusText.textContent = `Онлайн · ${user.first_name || "монтажник"} підключений`;
  }
}

// Стани
let currentStore = "A3175";
let currentUnit = "K1";
let currentUnitType = "24Н";

// Стандартні довжини, м (можеш підлаштувати)
const STANDARD_LENGTH_M = {
  "24Н": 7,
  "12Н": 3
};

// Елементи
const storeGrid = document.getElementById("store-grid");
const unitsGrid = document.getElementById("units-grid");
const formContext = document.getElementById("form-context");

const lineInput = document.getElementById("line-length-input");
const pumpCountSpan = document.getElementById("pump-count");
const solderCountSpan = document.getElementById("solder-count");

const stdLengthEl = document.getElementById("std-length");
const factLengthEl = document.getElementById("fact-length");
const overLengthEl = document.getElementById("over-length");
const chargeR32El = document.getElementById("charge-r32");

const submitBtn = document.getElementById("submit-btn");

// 1. Перемикання магазинів
storeGrid.addEventListener("click", (e) => {
  const chip = e.target.closest(".store-chip");
  if (!chip) return;

  document.querySelectorAll(".store-chip").forEach(c => c.classList.remove("active"));
  chip.classList.add("active");

  currentStore = chip.dataset.store;
  updateFormContext();
});

// 2. Перемикання K1–K5
unitsGrid.addEventListener("click", (e) => {
  const card = e.target.closest(".unit-card");
  if (!card) return;

  document.querySelectorAll(".unit-card").forEach(c => c.classList.remove("active"));
  card.classList.add("active");

  currentUnit = card.dataset.unit;
  currentUnitType = card.dataset.type || "24Н";
  updateFormContext();
  updateAnalytics();
});

// 3. Лічильники насоса / пайки
document.addEventListener("click", (e) => {
  const btn = e.target.closest(".field-btn");
  if (!btn) return;

  const target = btn.dataset.target;
  const op = btn.dataset.op;

  if (target === "pump") {
    let val = parseInt(pumpCountSpan.textContent, 10) || 0;
    val = op === "inc" ? val + 1 : Math.max(0, val - 1);
    pumpCountSpan.textContent = String(val);
  }

  if (target === "solder") {
    let val = parseInt(solderCountSpan.textContent, 10) || 0;
    val = op === "inc" ? val + 1 : Math.max(0, val - 1);
    solderCountSpan.textContent = String(val);
  }
});

// 4. Перерахунок аналітики при зміні довжини
lineInput.addEventListener("input", () => {
  updateAnalytics();
});

function updateFormContext() {
  formContext.textContent = `${currentStore} · ${currentUnit} (${currentUnitType})`;
  updateAnalytics();
}

function updateAnalytics() {
  const lengthMm = parseFloat(lineInput.value || "0");
  const lengthM = lengthMm / 1000;
  const std = STANDARD_LENGTH_M[currentUnitType] ?? 7;

  const over = Math.max(0, lengthM - std);
  const chargePerM = 35; // г на метр – підлаштуєш під модель
  const charge = over * chargePerM;

  stdLengthEl.textContent = `${std.toFixed(1)} м`;
  factLengthEl.textContent = `${lengthM.toFixed(1)} м`;
  overLengthEl.textContent = `${over.toFixed(1)} м`;
  chargeR32El.textContent = `${Math.round(charge)} г`;
}

// 5. Відправка даних в бота
submitBtn.addEventListener("click", () => {
  const lengthMm = parseFloat(lineInput.value || "0");
  const lengthM = lengthMm / 1000;
  const pumps = parseInt(pumpCountSpan.textContent, 10) || 0;
  const solder = parseInt(solderCountSpan.textContent, 10) || 0;

  const std = STANDARD_LENGTH_M[currentUnitType] ?? 7;
  const over = Math.max(0, lengthM - std);
  const chargePerM = 35;
  const charge = over * chargePerM;

  const payload = {
    action: "save_installation",
    store_code: currentStore,
    unit_code: currentUnit,
    unit_type: currentUnitType,
    line_length_m: Number(lengthM.toFixed(2)),
    pumps_count: pumps,
    solder_points: solder,
    std_length_m: std,
    over_length_m: Number(over.toFixed(2)),
    charge_r32_g: Math.round(charge)
  };

  if (tg) {
    tg.sendData(JSON.stringify(payload));
    // Можна одразу закрити WebApp, якщо хочеш:
    // tg.close();
  } else {
    // Для тесту в браузері без Telegram
    console.log("DEBUG payload:", payload);
    alert("Дані, які пішли б у бота:\n" + JSON.stringify(payload, null, 2));
  }
});

// Стартові значення
updateFormContext();
updateAnalytics();

