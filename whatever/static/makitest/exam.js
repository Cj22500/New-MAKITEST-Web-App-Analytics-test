"use strict";
const exam = document.getElementById("exam"),
  form = document.getElementById("exam-form");
// Every document has its own lease; a refresh can rotate the previous lease.
const storageKey = `makitest-writer-${exam.dataset.attempt}`;
const previousToken =
  performance.getEntriesByType("navigation")[0]?.type === "reload"
    ? sessionStorage.getItem(storageKey)
    : null;
let token = crypto.randomUUID().replaceAll("-", "");
document.getElementById("writer-token").value = token;
let expiry = Date.parse(exam.dataset.expiry),
  offset = Date.parse(exam.dataset.now) - Date.now();
let active = false,
  submitting = false,
  dirty = false,
  saveTimer,
  saveQueue = Promise.resolve(),
  camera;
const fields = () => [...form.querySelectorAll("[name^=question_]")];
fields().forEach((field) => (field.disabled = true));
function answers() {
  const result = {};
  for (const field of fields()) {
    const id = field.name.replace("question_", "");
    if (!(id in result)) result[id] = "";
    if (field.type !== "radio" || field.checked) result[id] = field.value;
  }
  return result;
}
function updateProgress() {
  const values = answers(),
    count = Object.values(values).filter((value) => value.trim()).length;
  document.getElementById("answered-count").textContent =
    `${count} of ${Object.keys(values).length} answered`;
  document.querySelectorAll("[data-jump]").forEach((link) => {
    const answered = !!values[link.dataset.jump].trim();
    link.classList.toggle("answered", answered);
    link.setAttribute(
      "aria-label",
      `Question ${link.textContent}: ${answered ? "answered" : "unanswered"}`,
    );
  });
}
function conflict() {
  active = false;
  camera?.stop();
  document.getElementById("writer-conflict").hidden = false;
  fields().forEach((field) => (field.disabled = true));
  document.getElementById("review-submit").disabled = true;
  document.getElementById("save-status").textContent =
    "Read-only: another tab is controlling this attempt.";
}
async function claim(takeover = false) {
  try {
    const state = await Makitest.json(exam.dataset.state, {
      token,
      takeover,
      previous_token: takeover ? null : previousToken,
    });
    if (state.completed) {
      location.href = state.results_url;
      return;
    }
    sessionStorage.setItem(storageKey, token);
    expiry = Date.parse(state.expires_at);
    offset = Date.parse(state.server_now) - Date.now();
    for (const field of fields()) {
      const value = state.answers[field.name.replace("question_", "")] || "";
      if (field.type === "radio") field.checked = field.value === value;
      else field.value = value;
      field.disabled = false;
    }
    dirty = false;
    updateProgress();
    active = true;
    document.getElementById("review-submit").disabled = false;
    document.getElementById("writer-conflict").hidden = true;
    document.getElementById("save-status").textContent = "Saved";
    startCamera();
  } catch (error) {
    if (error.status === 409) conflict();
    else document.getElementById("save-status").textContent = error.message;
  }
}
function save() {
  if (!active || submitting) return saveQueue;
  const snapshot = answers();
  document.getElementById("save-status").textContent = "Saving…";
  saveQueue = saveQueue
    .catch(() => {})
    .then(async () => {
      try {
        await Makitest.json(exam.dataset.save, { token, answers: snapshot });
        if (JSON.stringify(answers()) === JSON.stringify(snapshot)) {
          dirty = false;
          document.getElementById("save-status").textContent = "Saved";
        }
      } catch (error) {
        if (error.status === 409 && Date.now() + offset < expiry) conflict();
        else
          document.getElementById("save-status").textContent =
            "Couldn’t save. Unsaved answers remain in this tab. Check your connection.";
      }
    });
  return saveQueue;
}
form.addEventListener("input", () => {
  if (!active || submitting) return;
  dirty = true;
  document.getElementById("save-status").textContent = "Unsaved changes";
  updateProgress();
  clearTimeout(saveTimer);
  saveTimer = setTimeout(save, 500);
});
form.addEventListener("change", () => {
  if (active) {
    dirty = true;
    document.getElementById("save-status").textContent = "Unsaved changes";
    updateProgress();
    clearTimeout(saveTimer);
    saveTimer = setTimeout(save, 500);
  }
});
document.querySelectorAll("[data-clear]").forEach(
  (button) =>
    (button.onclick = () => {
      if (!active || submitting) return;
      form
        .querySelectorAll(`[name="question_${button.dataset.clear}"]`)
        .forEach((field) => {
          if (field.type === "radio") field.checked = false;
          else field.value = "";
        });
      dirty = true;
      document.getElementById("save-status").textContent = "Unsaved changes";
      updateProgress();
      clearTimeout(saveTimer);
      saveTimer = setTimeout(save, 500);
    }),
);
document.getElementById("takeover").onclick = () => {
  token = crypto.randomUUID().replaceAll("-", "");
  sessionStorage.setItem(storageKey, token);
  document.getElementById("writer-token").value = token;
  claim(true);
};
function startCamera() {
  camera?.stop();
  camera = new CameraLink({
    session: exam.dataset.session,
    phase: "exam",
    token,
    video: document.getElementById("video"),
    device: exam.dataset.camera || "",
    onstatus: (text) =>
      (document.getElementById("camera-status").textContent = text),
  });
  camera.connect();
  camera.enable();
}
document.getElementById("retry-camera").onclick = () => {
  if (active) {
    if (!camera.serverReady) camera.connect();
    camera.enable();
  }
};
document.getElementById("review-submit").onclick = () => {
  const values = Object.values(answers()),
    count = values.filter((value) => value.trim()).length;
  document.getElementById("review-summary").textContent =
    `${count} answered · ${values.length - count} unanswered. Unanswered questions receive no points.`;
  document.getElementById("submit-dialog").showModal();
};
async function submit() {
  if (!active || submitting) return;
  submitting = true;
  clearTimeout(saveTimer);
  document.getElementById("review-submit").disabled = true;
  document.getElementById("confirm-submit").disabled = true;
  document.getElementById("submit-dialog").close();
  document.getElementById("save-status").textContent = "Submitting your exam…";
  // Freeze the final snapshot before waiting for queued saves or tracker finalization.
  const finalAnswers = answers();
  fields().forEach((field) => (field.disabled = true));
  await saveQueue.catch(() => {});
  const body = new FormData(form);
  for (const [id, value] of Object.entries(finalAnswers))
    body.set("question_" + id, value);
  // Persist final values while still within the deadline, before the evidence wait.
  if (Date.now() + offset < expiry) {
    try {
      await Makitest.json(exam.dataset.save, { token, answers: finalAnswers });
    } catch (error) {
      if (error.status === 409 && Date.now() + offset < expiry) {
        submitting = false;
        conflict();
        return;
      }
    }
  }
  await camera?.finalize();
  try {
    const response = await fetch(form.action, {
      method: "POST",
      body,
      headers: { "X-CSRFToken": Makitest.csrf() },
    });
    if (!response.ok) throw new Error();
    if (response.redirected) {
      location.href = response.url;
      return;
    }
    throw new Error();
  } catch {
    submitting = false;
    fields().forEach((field) => (field.disabled = false));
    document.getElementById("review-submit").disabled = false;
    document.getElementById("confirm-submit").disabled = false;
    document.getElementById("save-status").textContent =
      "Submission could not be confirmed. Check your connection, then retry. Saved answers remain on the server.";
  }
}
form.addEventListener("submit", (event) => {
  event.preventDefault();
  document.getElementById("review-submit").click();
});
document.getElementById("confirm-submit").onclick = submit;
document.getElementById("leave").onclick = async () => {
  clearTimeout(saveTimer);
  if (dirty) await save();
  document.getElementById("leave-save-state").textContent = dirty
    ? "Some answers could not be saved. Staying in this tab lets you retry."
    : "Your answers have been saved.";
  document.getElementById("leave-dialog").showModal();
};
let warnedFive = false,
  warnedOne = false;
function tick() {
  const remaining = Math.max(
      0,
      Math.ceil((expiry - Date.now() - offset) / 1000),
    ),
    timer = document.getElementById("timer");
  timer.textContent = `${Math.floor(remaining / 60)}:${String(remaining % 60).padStart(2, "0")}`;
  timer.classList.toggle("warn", remaining <= 300);
  timer.classList.toggle("danger", remaining <= 60);
  if (remaining <= 300 && !warnedFive) {
    warnedFive = true;
    document.getElementById("save-status").textContent =
      "Five minutes or less remain. Review your answers.";
  }
  if (remaining <= 60 && !warnedOne) {
    warnedOne = true;
    document.getElementById("save-status").textContent =
      "One minute or less remains. Your exam will submit at the deadline.";
  }
  if (!remaining && active && !submitting) submit();
}
setInterval(tick, 1000);
tick();
updateProgress();
claim();
setInterval(async () => {
  if (!active || submitting) return;
  try {
    const response = await fetch(`${exam.dataset.state}?token=${token}`);
    if (response.status === 409) {
      conflict();
      return;
    }
    if (!response.ok) return;
    const state = await response.json();
    expiry = Date.parse(state.expires_at);
    offset = Date.parse(state.server_now) - Date.now();
    if (state.completed) {
      location.href = state.results_url;
      return;
    }
    if (dirty) save();
  } catch {
    /* retain dirty work and retry on the next heartbeat */
  }
}, 10000);
window.addEventListener("beforeunload", (event) => {
  if (dirty && !submitting) {
    event.preventDefault();
    event.returnValue = "";
  }
});
window.addEventListener("pagehide", () => camera?.stop());
function report(keys) {
  if (active && !submitting) camera?.send({ type: "keystrokes", keys });
}
document.addEventListener("keydown", (event) => {
  const keys = [];
  if (event.ctrlKey && ["c", "v"].includes(event.key.toLowerCase()))
    keys.push("ctrl+" + event.key.toLowerCase());
  if (event.altKey && event.key === "Tab") keys.push("alt+tab");
  if (event.metaKey && event.key === "Tab") keys.push("cmd+tab");
  if (event.key === "F11") keys.push("f11");
  if (event.key === "PrintScreen") keys.push("print_screen");
  if (keys.length) report(keys);
});
window.addEventListener("blur", () => report(["window_focus_lost"]));
document.addEventListener("visibilitychange", () => {
  if (document.hidden) report(["tab_hidden"]);
});
