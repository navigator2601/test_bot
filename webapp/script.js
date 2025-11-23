// Telegram WebApp
const tg = window.Telegram ? window.Telegram.WebApp : null;

if (tg) {
  tg.expand();
}

// ===== 1. Годинник =====

function updateClock() {
  const now = new Date();
  const d = now.toLocaleDateString("uk-UA");
  const t = now.toLocaleTimeString("uk-UA", { hour: "2-digit", minute: "2-digit" });
  const el = document.getElementById("datetime");
  if (el) el.textContent = `${d} · ${t}`;
}

setInterval(updateClock, 1000);
updateClock();

// ===== 2. Доступи користувача (поки мок) =====
// Потім це замінимо на запит до бекенда / БД

const mockUser = {
  access_level: 2,   // 0 – гість, 1 – довірений, 2 – продвинутий
  is_admin: true     // true – бачить адмін-модуль
};

// якщо є хоча б 1 рівень доступу — відкриваємо робочі модулі
if (mockUser.access_level >= 1) {
  const workGroup = document.getElementById("work-module-group");
  if (workGroup) workGroup.classList.remove("hidden");
}

// якщо адмін — показуємо адмін-модуль
if (mockUser.is_admin) {
  const adminGroup = document.getElementById("admin-module-group");
  if (adminGroup) adminGroup.classList.remove("hidden");
}

// ===== 3. Обробка кліків по блоках-модулях =====

document.addEventListener("click", (e) => {
  const block = e.target.closest(".rx-block");
  if (!block) return;

  const action = block.dataset.action;

  // Поки що – просто показуємо що натиснули.
  // Далі тут будуть переходи на інші екрани / tg.sendData тощо.
  if (!tg) {
    alert("Обраний модуль: " + action);
    return;
  }

  // Приклад payload до бота
  const payload = {
    action: "open_module",
    module: action
  };

  tg.sendData(JSON.stringify(payload));
  // tg.close(); // якщо треба закривати WebApp після вибору
});

// ===== 4. Прибрати splash з DOM після анімації =====

const splash = document.getElementById("splash");
setTimeout(() => {
  if (splash) splash.remove();
}, 5600);

if (tg) {
  tg.ready();
}

