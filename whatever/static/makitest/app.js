"use strict";
window.Makitest = {
  csrf() {
    return document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
  },
  async json(url, data) {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": this.csrf(),
      },
      body: JSON.stringify(data),
    });
    let body;
    try {
      body = await response.json();
    } catch {
      throw new Error("The server could not respond. Try again.");
    }
    if (!response.ok) {
      const error = new Error(
        body.error || "The request could not be completed.",
      );
      error.status = response.status;
      throw error;
    }
    return body;
  },
};
document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-enlarge]");
  if (!button) return;
  const source = button.querySelector("img"),
    dialog = document.getElementById("image-dialog");
  dialog.querySelector("img").src = source.src;
  dialog.querySelector("img").alt = source.alt;
  dialog.showModal();
});
class CameraLink {
  constructor({ session, phase, video, device, token, onmessage, onstatus }) {
    Object.assign(this, {
      session,
      phase,
      video,
      device,
      token,
      onmessage,
      onstatus,
    });
    this.canvas = document.createElement("canvas");
    this.canvas.width = 640;
    this.canvas.height = 480;
    this.ctx = this.canvas.getContext("2d");
    this.stopped = false;
    this.face = false;
    this.eyes = false;
  }
  connect() {
    if (this.stopped) return;
    if (
      this.ws &&
      [WebSocket.OPEN, WebSocket.CONNECTING].includes(this.ws.readyState)
    )
      return;
    clearTimeout(this.reconnect);
    this.onstatus("Connecting to monitoring…");
    this.ws = new WebSocket(
      `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws/proctor/${this.session}/?phase=${this.phase}&token=${this.token || ""}`,
    );
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "ready") {
        this.serverReady = true;
        this.send({ type: "camera_selected", camera_id: this.device || "" });
        this.onstatus(
          this.stream ? "Camera connected" : "Enable your camera to continue",
        );
      }
      if (data.type === "frame_result") {
        this.face = !!data.face_detected;
        this.eyes = !!data.eyes_detected;
        this.onstatus(
          this.face
            ? "Camera connected"
            : "Keep your face visible to the camera",
        );
      }
      if (data.type === "error") this.onstatus(data.message);
      if (data.type === "session_closed") {
        this.finishResolve?.(true);
      }
      this.onmessage?.(data);
    };
    this.ws.onclose = (event) => {
      this.serverReady = false;
      if (!this.stopped) {
        this.onstatus(
          "Monitoring disconnected. Your answers can still be saved.",
        );
        if (event.code !== 4403 && event.code !== 4500 && event.code !== 4409) {
          this.reconnect = setTimeout(() => this.connect(), 2000);
        }
      }
    };
    this.ws.onerror = () =>
      this.onstatus(
        "Monitoring connection unavailable. Check your connection.",
      );
  }
  send(data) {
    if (this.ws?.readyState === WebSocket.OPEN)
      this.ws.send(JSON.stringify(data));
  }
  async enable() {
    if (this.stream) this.stream.getTracks().forEach((track) => track.stop());
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: 640,
          height: 480,
          ...(this.device ? { deviceId: { exact: this.device } } : {}),
        },
        audio: false,
      });
      this.video.srcObject = this.stream;
      await this.video.play();
      this.device = this.stream.getVideoTracks()[0].getSettings().deviceId;
      this.send({ type: "camera_selected", camera_id: this.device || "" });
      this.stream.getVideoTracks()[0].onended = () =>
        this.onstatus(
          "Camera stopped. Reconnect your camera and choose Retry camera.",
        );
      if (!this.pump) this.pump = setInterval(() => this.capture(), 100);
      this.onstatus("Camera connected");
      return true;
    } catch (error) {
      const messages = {
        NotAllowedError:
          "Camera permission was denied. Allow camera access in your browser, then retry.",
        NotFoundError: "No camera was found. Connect a webcam, then retry.",
        NotReadableError:
          "Your camera is busy. Close the app using it, then retry.",
        OverconstrainedError:
          "The selected camera is unavailable. Select another camera.",
      };
      this.onstatus(
        messages[error.name] ||
          "Camera unavailable. Use localhost or HTTPS and check your browser camera settings.",
      );
      return false;
    }
  }
  capture() {
    if (
      !this.serverReady ||
      this.ws?.readyState !== WebSocket.OPEN ||
      !this.stream?.active ||
      this.video.readyState < 2 ||
      this.ws.bufferedAmount ||
      this.capturing
    )
      return;
    this.capturing = true;
    this.ctx.drawImage(this.video, 0, 0, 640, 480);
    this.canvas.toBlob(
      (blob) => {
        if (blob && this.ws?.readyState === WebSocket.OPEN) this.ws.send(blob);
        this.capturing = false;
      },
      "image/jpeg",
      0.7,
    );
  }
  async finalize() {
    this.stopped = true;
    clearTimeout(this.reconnect);
    clearInterval(this.pump);
    if (this.ws?.readyState !== WebSocket.OPEN) return false;
    return new Promise((resolve) => {
      const timeout = setTimeout(() => resolve(false), 30000);
      this.finishResolve = (value) => {
        clearTimeout(timeout);
        resolve(value);
      };
      this.send({ type: "finalize_session" });
    });
  }
  stop() {
    this.stopped = true;
    clearInterval(this.pump);
    clearTimeout(this.reconnect);
    this.stream?.getTracks().forEach((track) => track.stop());
    this.ws?.close(1000);
  }
}
window.CameraLink = CameraLink;
