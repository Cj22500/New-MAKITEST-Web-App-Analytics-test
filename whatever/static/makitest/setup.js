"use strict";
const setup = document.getElementById("setup"),
  stage = document.getElementById("calibration-stage");
const prompt = document.getElementById("cal-prompt"),
  status = document.getElementById("cal-status");
const progress = document.getElementById("cal-progress"),
  target = document.getElementById("target");
const next = document.getElementById("continue"),
  begin = document.getElementById("begin");
const directions = ["center", "top", "bottom", "left", "right"];
const coordinates = [
  ["50%", "50%"],
  ["50%", "24px"],
  ["50%", "calc(100% - 24px)"],
  ["24px", "50%"],
  ["calc(100% - 24px)", "50%"],
];
let mode = "idle",
  current = -1,
  pending = 0,
  calibrated = setup.dataset.finalized === "true",
  countdown;
const camera = new CameraLink({
  session: setup.dataset.session,
  phase: "setup",
  video: document.getElementById("video"),
  device: sessionStorage.getItem("makitest-camera") || "",
  onmessage: handle,
  onstatus: (text) => {
    document.getElementById("camera-status").textContent = text;
    begin.disabled = !(
      camera.face &&
      camera.serverReady &&
      camera.stream?.active
    );
    if (!camera.serverReady && stage.hidden === false)
      status.textContent =
        "Connection interrupted. Reconnect before continuing.";
  },
});
camera.connect();
function ready() {
  calibrated = true;
  mode = "ready";
  clearInterval(countdown);
  stage.close();
  stage.hidden = true;
  begin.hidden = true;
  document.getElementById("ready").hidden = false;
  document.getElementById("start-exam").focus();
}
if (calibrated) ready();
function handle(data) {
  const cal = data.calibration || (data.type === "calibration" ? data : null);
  if (!cal) return;
  if (cal.ok === false) {
    clearInterval(countdown);
    mode = current < 0 ? "baselineWaiting" : "pointWaiting";
    status.textContent =
      cal.message || "Keep your face visible and press Space to retry.";
    next.disabled = false;
    next.textContent = "Retry";
    return;
  }
  if (mode === "idle") {
    pending = cal.stage;
    calibrated = cal.calibrated;
    if (cal.calibrated) ready();
    return;
  }
  if (mode === "baseline" && cal.stage === 0) {
    showPoint(0);
    return;
  }
  if (cal.collecting) {
    mode = "collecting";
    progress.max = cal.needed;
    progress.value = cal.collected;
    status.textContent =
      "Keep looking at the target while this point is captured.";
    next.disabled = true;
    return;
  }
  if (mode === "collecting" && (cal.stage > current || cal.calibrated)) {
    progress.value = progress.max;
    pending = cal.stage;
    calibrated = cal.calibrated;
    mode = "pointComplete";
    next.disabled = false;
    const upcoming = directions[pending];
    next.textContent = calibrated
      ? "Finish setup"
      : `Continue: look at the ${upcoming}`;
    status.textContent = calibrated
      ? "Final point complete. Press Space to finish setup."
      : `Point complete. Press Space, then look at the ${upcoming} of the screen.`;
  }
}
function showPoint(index) {
  current = index;
  mode = "countdown";
  target.hidden = false;
  target.style.left = coordinates[index][0];
  target.style.top = coordinates[index][1];
  document.getElementById("step-count").textContent = `Point ${index + 1} of 5`;
  prompt.textContent =
    index === 0
      ? "Look at the center of the screen"
      : `Look at the ${directions[index]} of the screen`;
  next.textContent = `Looking at the ${directions[index]}…`;
  progress.value = 0;
  next.disabled = true;
  let seconds = 2;
  status.textContent =
    "Capture starts in 2 seconds. Keep looking at the target.";
  clearInterval(countdown);
  countdown = setInterval(() => {
    seconds--;
    if (seconds > 0) {
      status.textContent = `Capture starts in ${seconds} second.`;
      return;
    }
    clearInterval(countdown);
    if (
      !camera.serverReady ||
      !camera.face ||
      !camera.eyes ||
      !camera.stream?.active
    ) {
      mode = "pointWaiting";
      next.disabled = false;
      next.textContent = "Retry";
      status.textContent =
        "We need a clear view of your face and eyes. Adjust your position and press Space to retry.";
      return;
    }
    mode = "startingCapture";
    camera.send({ type: "calibrate_next" });
  }, 1000);
}
function advance() {
  if (!camera.serverReady || !camera.stream?.active) return;
  if (mode === "baselineWaiting") {
    mode = "baseline";
    next.disabled = true;
    camera.send({ type: "calibrate_next" });
  } else if (mode === "pointComplete") {
    if (calibrated) ready();
    else showPoint(pending);
  } else if (mode === "pointWaiting") showPoint(current);
}
begin.onclick = () => {
  stage.hidden = false;
  stage.showModal();
  stage.focus();
  target.hidden = true;
  progress.value = 0;
  next.disabled = false;
  next.textContent = "Continue";
  if (pending >= 0) {
    showPoint(pending);
  } else {
    mode = "baselineWaiting";
    current = -1;
    document.getElementById("step-count").textContent = "Starting position";
    prompt.textContent = "Look at the center of the screen";
    status.textContent =
      "Sit comfortably, look at the center of the screen, then press Space to set your starting position.";
    next.textContent = "Continue: look at the center";
    target.hidden = false;
    target.style.left = coordinates[0][0];
    target.style.top = coordinates[0][1];
  }
};
next.onclick = advance;
document.addEventListener("keydown", (event) => {
  if (
    event.code !== "Space" ||
    event.repeat ||
    stage.hidden ||
    event.target.closest("input,textarea,select,button,[contenteditable=true]")
  )
    return;
  event.preventDefault();
  advance();
});
document.getElementById("cancel").onclick = () => {
  clearInterval(countdown);
  camera.send({ type: "calibrate_pause" });
  stage.close();
  stage.hidden = true;
  mode = "idle";
};
stage.addEventListener("cancel", (event) => {
  event.preventDefault();
  document.getElementById("cancel").click();
});
document.getElementById("enable-camera").onclick = async () => {
  if (await camera.enable()) {
    document.getElementById("enable-camera").textContent = "Retry camera";
    sessionStorage.setItem("makitest-camera", camera.device);
    const devices = (await navigator.mediaDevices.enumerateDevices()).filter(
      (item) => item.kind === "videoinput",
    );
    const select = document.getElementById("camera-select");
    select.replaceChildren(
      ...devices.map((item, index) => {
        const option = document.createElement("option");
        option.value = item.deviceId;
        option.textContent = item.label || `Camera ${index + 1}`;
        option.selected = item.deviceId === camera.device;
        return option;
      }),
    );
  }
};
async function reset() {
  clearInterval(countdown);
  camera.stop();
  try {
    await Makitest.json(setup.dataset.reset, {});
    location.reload();
  } catch (error) {
    document.getElementById("camera-status").textContent = error.message;
  }
}
document.getElementById("camera-select").onchange = (event) => {
  sessionStorage.setItem("makitest-camera", event.target.value);
  reset();
};
document.getElementById("restart").onclick = reset;
document.getElementById("start-exam").onclick = async () => {
  const button = document.getElementById("start-exam");
  button.disabled = true;
  button.textContent = "Preparing exam…";
  if (setup.dataset.finalized === "true" || (await camera.finalize())) {
    document.getElementById("start-form").submit();
  } else {
    button.disabled = false;
    button.textContent = "Start exam";
    document.getElementById("camera-status").textContent =
      "Setup could not be confirmed. Restart setup before starting.";
  }
};
window.addEventListener("pagehide", () => camera.stop());
