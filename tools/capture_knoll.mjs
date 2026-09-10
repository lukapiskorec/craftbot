#!/usr/bin/env node
// Record the viewer's knolling sequence to an mp4: the model, then every
// element rearranged into stacked bundles, then flat on its widest face, then
// back to the model on the opening framing so the clip loops.
//
//   node tools/capture_knoll.mjs [options]      (--help for the option list)
//
// Headless Chrome renders the real viewer (viewer/index.html, ?debug=1), a CDP
// driver choreographs it and every frame is grabbed with Page.captureScreenshot,
// then ffmpeg stitches the PNGs.
//
// The one trick that makes this work: performance.now() is frozen at page start
// and stepped by exactly 1/fps per frame. Both time sources the viewer animates
// on - THREE.Clock in the render loop (animations.js) and the camera flight in
// views.js - read it, so the recording is frame-exact and independent of how
// fast headless actually paints. Playing the animation in real time and grabbing
// what you can does not work: --virtual-time-budget never gets past ~7 % of the
// transition. CSS animations are a separate timeline and are pinned by hand.
//
// Needs Chrome (CRAFTBOT_CHROME, or the default install path), python for the
// static server, and ffmpeg on PATH.

import { spawn, spawnSync } from "node:child_process";
import { mkdirSync, rmSync, writeFileSync, readdirSync, existsSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";

const REPO = path.resolve(import.meta.dirname, "..");
const CHROME_DEFAULT = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

// viewer/js/styles.js
const STYLES = ["plaster", "solid", "random", "mono", "wireframe", "blueprint", "dither"];

// viewer/js/knolling.js
const ARRANGEMENTS = ["model", "flat", "stacked"];

// Named view directions, as the navigation cube snaps them: a face, an edge or
// a corner of the cube. `axo` is the viewer's own three-quarter view.
const DIRECTIONS = {
  top: [0, 0, 1], bottom: [0, 0, -1],
  front: [0, -1, 0], back: [0, 1, 0], left: [-1, 0, 0], right: [1, 0, 0],
  "top-front": [0, -1, 1], "top-back": [0, 1, 1],
  "top-left": [-1, 0, 1], "top-right": [1, 0, 1],
  "front-left": [-1, -1, 0], "front-right": [1, -1, 0],
  "top-front-left": [-1, -1, 1], "top-front-right": [1, -1, 1],
  axo: [1, -1, 0.8],
};

// The length main.js gives a knolling transition. --transition stretches it by
// wrapping anims.startKnoll, and the camera flights alongside it stretch to match.
const VIEWER_KNOLL_SECONDS = 3;

// ---- options -------------------------------------------------------------
// name: [default, help]. A boolean default makes a flag (--loop / --no-loop),
// a number default parses as a number, null means "worked out below".
const OPTIONS = {
  model: ["08_The_Segal_Method_Blender_Python/fable_v06.json", "model file under viewer/models/"],
  style: ["mono", `render style: ${STYLES.join(", ")}`],
  mode: [0, "style variant: 0 light, 1 dark for mono, wireframe and dither; re-rolls random's palette"],
  "model-view": ["axo", "direction the model is seen from"],
  "stacked-view": ["top-front", "direction the stacked arrangement is seen from"],
  "flat-view": ["top", "direction the flat arrangement is seen from"],
  sequence: ["model,stacked,flat", `arrangements to visit, in order; the clip opens on the first`],
  lock: ["", `hold one arrangement's framing for the whole clip (${ARRANGEMENTS.join(", ")}), `
    + "so only the geometry moves; default: the camera flies to each in turn"],
  zoom: [1, "magnify the framing: 1.2 draws it 20 % bigger than the fit"],
  transition: [VIEWER_KNOLL_SECONDS, "seconds one arrangement takes to become the next"],
  hold: [1.0, "seconds held on each arrangement (with --loop the opening beat holds 60 % of it)"],
  loop: [true, "end back on the arrangement the clip opened on, framed as the first beat"],
  fps: [30, "frames per second"],
  width: [1344, "frame width in CSS px"],
  height: [1080, "frame height in CSS px"],
  scale: [2, "pixel ratio to render at; frames are downsampled to width x height"],
  out: [null, "output file (default: outputs/knolling_<model>_<timestamp>.mp4)"],
  frames: [null, "where to write the PNG frames (default: a temp folder)"],
  "keep-frames": [false, "keep the frames after stitching"],
  port: [8123, "port for the local static server"],
};

function usage() {
  const rows = Object.entries(OPTIONS).map(([name, [def, help]]) => {
    const flag = typeof def === "boolean" ? `--${name}` : `--${name} <v>`;
    const shown = def === null || def === false || def === "" ? "" : ` (${def})`;
    return `  ${flag.padEnd(20)} ${help}${shown}`;
  });
  return [
    "Record the viewer's knolling sequence to an mp4.",
    "",
    "  node tools/capture_knoll.mjs [options]",
    "",
    ...rows,
    "  --help               this text",
    "",
    `Views: ${Object.keys(DIRECTIONS).join(", ")}`,
    "Needs Chrome (CRAFTBOT_CHROME), python and ffmpeg on PATH.",
  ].join("\n");
}

const camel = (s) => s.replace(/-([a-z])/g, (_, ch) => ch.toUpperCase());

function parseArgs(argv) {
  const opt = {};
  for (const [name, [def]] of Object.entries(OPTIONS)) opt[camel(name)] = def;
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "--help" || arg === "-h") { console.log(usage()); process.exit(0); }
    if (!arg.startsWith("--")) throw new Error(`unexpected argument ${arg}`);
    const negated = arg.startsWith("--no-");
    const name = negated ? arg.slice(5) : arg.slice(2);
    if (!(name in OPTIONS)) throw new Error(`unknown option ${arg} (--help for the list)`);
    const def = OPTIONS[name][0];
    if (typeof def === "boolean") opt[camel(name)] = !negated;
    else if (negated) throw new Error(`${arg} takes a value, drop the no-`);
    else opt[camel(name)] = typeof def === "number" ? Number(argv[++i]) : argv[++i];
  }

  if (!STYLES.includes(opt.style)) throw new Error(`unknown style ${opt.style}: ${STYLES.join(", ")}`);
  for (const key of ["modelView", "stackedView", "flatView"]) {
    if (!(opt[key] in DIRECTIONS)) {
      throw new Error(`unknown view ${opt[key]}: ${Object.keys(DIRECTIONS).join(", ")}`);
    }
  }
  for (const key of ["mode", "zoom", "transition", "hold", "fps", "width", "height", "scale", "port"]) {
    if (!Number.isFinite(opt[key])) throw new Error(`--${key} needs a number`);
  }
  if (opt.fps < 1 || opt.hold < 0 || opt.width < 1 || opt.height < 1 || opt.scale < 1) {
    throw new Error("fps, width, height and scale must be positive, hold non-negative");
  }
  if (opt.zoom <= 0 || opt.transition <= 0) throw new Error("zoom and transition must be positive");
  if (opt.lock && !ARRANGEMENTS.includes(opt.lock)) {
    throw new Error(`unknown arrangement ${opt.lock}: ${ARRANGEMENTS.join(", ")}`);
  }
  opt.sequence = opt.sequence.split(",").map((s) => s.trim()).filter(Boolean);
  if (!opt.sequence.length) throw new Error("--sequence needs at least one arrangement");
  for (const name of opt.sequence) {
    if (!ARRANGEMENTS.includes(name)) {
      throw new Error(`unknown arrangement ${name}: ${ARRANGEMENTS.join(", ")}`);
    }
  }
  opt.out ??= path.join(REPO, "outputs", `knolling_${slug(opt.model)}_${stamp()}.mp4`);
  opt.frames ??= path.join(tmpdir(), "craftbot-knoll-frames");
  return opt;
}

// "08_The_Segal_Method_Blender_Python/fable_v06.json" -> "exp08_fable_v06"
function slug(model) {
  const [dir, file] = model.split("/");
  return `exp${dir.slice(0, 2)}_${path.basename(file, ".json")}`;
}

// Local time, so runs of the same model sort and never overwrite each other.
function stamp() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}`
    + `-${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`;
}

// ---- the shot list -------------------------------------------------------
// One beat per row: a hold, or an action evaluated in the page (awaited before
// the clock starts moving again) followed by `seconds` of stepped time. Each
// transition is one camera flight, landing framed on the arrangement from its
// own direction in KNOLL_VIEW - unless --lock, which pins one framing and lets
// the geometry move through it.
//
// With --loop the closing beat returns to the arrangement the clip opened on,
// on the opening framing. Coming home to the model, __frameBounds hands that
// flight the scene bounds the opening frame was built from: knolling's own model
// layout bounds are the union of oriented-box AABBs, a hair wider than the real
// geometry, and would show as a jump.
function storyboard(opt) {
  const seq = opt.sequence;
  const view = (name) => (opt.lock ? `locked on ${opt.lock}` : opt[`${name}View`]);
  const hold = (name, seconds) => ({ label: `${name} (${view(name)})`, seconds });
  const goTo = (name) => ({
    label: `-> ${name}`, seconds: opt.transition,
    action: `window.craftbot.arrange(${JSON.stringify(name)})`,
  });

  const beats = [hold(seq[0], opt.hold * (opt.loop ? 0.6 : 1))];
  for (const name of seq.slice(1)) beats.push(goTo(name), hold(name, opt.hold));

  const home = seq[0];
  if (!opt.loop || seq[seq.length - 1] === home) return beats;
  const back = home !== "model" ? goTo(home) : {
    label: "-> model", seconds: opt.transition, action: `(async () => {
        window.__frameBounds = window.craftbot.getSceneApi().bounds;
        await window.craftbot.arrange("model");
        window.__frameBounds = null;
      })()` };
  return beats.concat(back, hold(home, opt.hold));
}

// Frozen clock, installed before any page script runs. `elapsed` is the video's
// own time, which the CSS animations are driven off too.
const CLOCK_SHIM = `
(() => {
  const real = performance.now.bind(performance);
  let t = real();
  const t0 = t;
  performance.now = () => t;
  window.__clock = {
    get t() { return t; }, get elapsed() { return t - t0; }, advance(ms) { t += ms; },
  };
})();
`;

// Collapse the rationale column (it owns 24rem of the width), aim each
// arrangement, and frame the opening one the way every later arrangement will be
// framed - projected extent, not the looser sphere fit loadModel() lands on. An
// opening arrangement other than the model is already in place by now: the URL
// carries ?knoll=<name>&kt=1, the viewer's own path for landing in one settled.
//
// frameTo is wrapped rather than main.js changed: every flight then uses the
// recording's insets instead of frameInsets(). The viewer keeps 14rem down the
// right for the band labels, which this clip never shows, and on a narrow frame
// that strip is what limits how big the flat sheet can be drawn.
function setupExpr(opt) {
  const dirs = {
    model: DIRECTIONS[opt.modelView],
    stacked: DIRECTIONS[opt.stackedView],
    flat: DIRECTIONS[opt.flatView],
  };
  const start = opt.sequence[0];
  const timeScale = opt.transition / VIEWER_KNOLL_SECONDS; // flights keep pace with the knoll
  return `(async () => {
    const c = window.craftbot;
    document.querySelector("#doc:not(.closed) > h2")?.click();
    Object.assign(c.KNOLL_VIEW, ${JSON.stringify(dirs)});
    const rem = parseFloat(getComputedStyle(document.documentElement).fontSize);
    const insets = {
      left: document.getElementById("gui").getBoundingClientRect().width,
      right: 7 * rem, // the view cube column, as main.js measures it
    };
    // Zoom rides on the bounds: framing() fits their projected extent, so a box
    // shrunk about its own centre by 1/zoom is drawn that many times bigger.
    const zoomed = (box) => {
      const out = box.clone();
      const mid = out.getCenter(new c.THREE.Vector3());
      out.min.lerp(mid, 1 - 1 / ${opt.zoom});
      out.max.lerp(mid, 1 - 1 / ${opt.zoom});
      return out;
    };
    const frameTo = c.views.frameTo.bind(c.views);
    c.views.frameTo = (bounds, dir, seconds, opts = {}) =>
      frameTo(zoomed(window.__frameBounds ?? bounds), dir, seconds * ${timeScale},
        { ...opts, midBounds: opts.midBounds ? zoomed(opts.midBounds) : null, insets });
    // A longer transition than main.js hands out, the same way: wrap, don't patch.
    const startKnoll = c.anims.startKnoll.bind(c.anims);
    c.anims.startKnoll = (sceneApi, from, to, delays, opts) =>
      startKnoll(sceneApi, from, to, delays, { ...opts, duration: ${opt.transition} });
    await new Promise((r) => requestAnimationFrame(r));
    const start = ${JSON.stringify(start)};
    const banner = document.getElementById("banner");
    if (!banner.hidden) return banner.textContent;
    if (c.knolling.toName !== start) return \`opened on \${c.knolling.toName}, not \${start}\`;
    // The opening frame, and with --lock the only frame: an arrangement other
    // than the model is framed on its own layout, which exists once it is solved.
    const framed = ${JSON.stringify(opt.lock || start)};
    const b = framed === "model" ? null : (c.knolling.layouts ?? {})[framed]?.bounds;
    if (framed !== "model" && !b) return \`no \${framed} layout to lock to; open the clip on it\`;
    const bounds = b
      ? new c.THREE.Box3(new c.THREE.Vector3(...b.min), new c.THREE.Vector3(...b.max))
      : c.getSceneApi().bounds;
    c.views.frameTo(bounds, new c.THREE.Vector3(...${JSON.stringify(dirs[opt.lock || start])}), 0);
    await new Promise((r) => requestAnimationFrame(r));
    if (${JSON.stringify(!!opt.lock)}) c.views.frameTo = () => {}; // every later flight is dropped
    return "ok";
  })()`;
}

// One stepped frame: move the frozen clock on, let the render loop draw it
// (twice - the second pass sees dt 0 and settles), then the caller grabs the
// surface. The render loop feeds anims.tick a delta clamped to 0.1 s (main.js),
// so a frame longer than that would stall the knolling while the camera flight,
// which reads performance.now() straight, ran on: sub-step under the clamp.
function stepExpr(fps) {
  const dt = 1000 / fps;
  const subSteps = Math.ceil(dt / 100);
  return `(async () => {
    const raf = () => Promise.race([
      new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))),
      new Promise((r) => setTimeout(r, 2000)),
    ]);
    for (let i = 0; i < ${subSteps}; i++) {
      window.__clock.advance(${dt / subSteps});
      // CSS animations (the blinking cursor in the GUI header) run on the
      // document timeline, which the frozen clock does not touch - left alone
      // they sample real time and flicker at the capture rate. Pin them to the
      // video's own clock so the 1.1 s blink is a 1.1 s blink on playback.
      for (const a of document.getAnimations()) {
        a.pause();
        a.currentTime = window.__clock.elapsed;
      }
      await raf();
    }
  })()`;
}

// ---- CDP -----------------------------------------------------------------

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function waitFor(what, fn, { timeout = 30000, every = 200 } = {}) {
  const deadline = Date.now() + timeout;
  for (;;) {
    try {
      const v = await fn();
      if (v) return v;
    } catch { /* not up yet */ }
    if (Date.now() > deadline) throw new Error(`timed out waiting for ${what}`);
    await sleep(every);
  }
}

function connect(wsUrl) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl);
    const pending = new Map();
    let seq = 0;
    ws.addEventListener("message", (ev) => {
      const msg = JSON.parse(ev.data);
      const p = pending.get(msg.id);
      if (!p) return;
      pending.delete(msg.id);
      if (msg.error) p.reject(new Error(msg.error.message));
      else p.resolve(msg.result);
    });
    ws.addEventListener("error", () => reject(new Error(`cannot connect to ${wsUrl}`)));
    ws.addEventListener("open", () => resolve({
      send(method, params = {}) {
        return new Promise((res, rej) => {
          const id = ++seq;
          pending.set(id, { resolve: res, reject: rej });
          ws.send(JSON.stringify({ id, method, params }));
        });
      },
      close: () => ws.close(),
    }));
  });
}

async function evaluate(cdp, expression, awaitPromise = false) {
  const r = await cdp.send("Runtime.evaluate", { expression, awaitPromise, returnByValue: true });
  if (r.exceptionDetails) {
    throw new Error(r.exceptionDetails.exception?.description ?? r.exceptionDetails.text);
  }
  return r.result.value;
}

// ---- main ----------------------------------------------------------------

async function capture(opt, chrome) {
  rmSync(opt.frames, { recursive: true, force: true });
  mkdirSync(opt.frames, { recursive: true });
  const profile = path.join(tmpdir(), `craftbot-knoll-profile-${process.pid}`);

  const server = spawn("python", ["-m", "http.server", "-d", path.join(REPO, "viewer"), String(opt.port)],
    { stdio: "ignore" });
  const start = opt.sequence[0];
  const url = `http://127.0.0.1:${opt.port}/?model=models/${opt.model}`
    + `&style=${opt.style}&mode=${opt.mode}&anim=none&debug=1&open=ANIMATION,SECTION`
    + (start === "model" ? "" : `&knoll=${start}&kt=1`);

  const browser = spawn(chrome, [
    "--headless=new", "--hide-scrollbars", "--no-first-run", "--no-default-browser-check",
    `--window-size=${opt.width},${opt.height}`,
    "--remote-debugging-port=9223", `--user-data-dir=${profile}`,
    "--disable-backgrounding-occluded-windows", "--disable-renderer-backgrounding",
    "--disable-features=CalculateNativeWinOcclusion",
    "about:blank",
  ], { stdio: "ignore" });

  let cdp = null;
  try {
    await waitFor("the static server", async () =>
      (await fetch(`http://127.0.0.1:${opt.port}/index.html`)).ok);
    const target = await waitFor("a Chrome page target", async () => {
      const list = await (await fetch("http://127.0.0.1:9223/json/list")).json();
      return list.find((t) => t.type === "page")?.webSocketDebuggerUrl;
    });
    cdp = await connect(target);
    await cdp.send("Page.enable");
    await cdp.send("Runtime.enable");
    await cdp.send("Emulation.setDeviceMetricsOverride", {
      width: opt.width, height: opt.height, deviceScaleFactor: opt.scale, mobile: false,
    });
    await cdp.send("Page.addScriptToEvaluateOnNewDocument", { source: CLOCK_SHIM });

    console.log(`loading ${url}`);
    await cdp.send("Page.navigate", { url });
    await waitFor("the model to load", () =>
      evaluate(cdp, `!!(window.craftbot && window.craftbot.getModel() && window.craftbot.getSceneApi())`));
    await evaluate(cdp, `document.fonts.ready`, true);
    if (start !== "model") { // ?knoll= solves the layouts before it arranges
      await waitFor(`the ${start} arrangement`, () =>
        evaluate(cdp, `window.craftbot.knolling.toName === ${JSON.stringify(start)}`));
    }
    await sleep(1200); // shader compile + the rationale fetch, on the real clock

    const setup = await evaluate(cdp, setupExpr(opt), true);
    if (setup !== "ok") throw new Error(`viewer error banner: ${setup}`);
    console.log(`${await evaluate(cdp, `window.craftbot.getModel().count`)} elements, `
      + `${opt.style} style, ${opt.width}x${opt.height} at ${opt.fps} fps`);

    const step = stepExpr(opt.fps);
    let n = 0;
    const t0 = Date.now();
    for (const beat of storyboard(opt)) {
      if (beat.action) await evaluate(cdp, beat.action, true);
      const count = Math.round(beat.seconds * opt.fps);
      for (let i = 0; i < count; i++) {
        await evaluate(cdp, step, true);
        const shot = await cdp.send("Page.captureScreenshot", { format: "png", fromSurface: true });
        writeFileSync(path.join(opt.frames, `f${String(n).padStart(5, "0")}.png`),
          Buffer.from(shot.data, "base64"));
        n++;
      }
      console.log(`  ${beat.label.padEnd(24)} ${count} frames (${n} total)`);
    }
    console.log(`captured ${n} frames in ${((Date.now() - t0) / 1000).toFixed(1)} s`);
  } finally {
    try { if (cdp) await cdp.send("Browser.close"); } catch { /* already gone */ }
    if (cdp) cdp.close();
    browser.kill();
    server.kill();
    if (process.platform === "win32") {
      spawnSync("taskkill", ["/PID", String(browser.pid), "/T", "/F"], { stdio: "ignore" });
    }
  }
}

function stitch(opt) {
  const shots = readdirSync(opt.frames).filter((f) => f.endsWith(".png"));
  if (!shots.length) throw new Error("no frames captured");
  const bytes = shots.reduce((a, f) => a + statSync(path.join(opt.frames, f)).size, 0);
  console.log(`stitching ${shots.length} frames (${(bytes / 1e6).toFixed(0)} MB) -> ${opt.out}`);
  mkdirSync(path.dirname(opt.out), { recursive: true });
  const ff = spawnSync("ffmpeg", [
    "-y", "-framerate", String(opt.fps), "-i", path.join(opt.frames, "f%05d.png"),
    "-vf", `scale=${opt.width}:${opt.height}:flags=lanczos,format=yuv420p`,
    "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-movflags", "+faststart",
    opt.out,
  ], { stdio: ["ignore", "ignore", "pipe"], encoding: "utf8" });
  if (ff.status !== 0) throw new Error(`ffmpeg failed:\n${(ff.stderr ?? "").slice(-1500)}`);
  if (!opt.keepFrames) rmSync(opt.frames, { recursive: true, force: true });
  console.log(`${opt.out} (${(statSync(opt.out).size / 1e6).toFixed(1)} MB, `
    + `${(shots.length / opt.fps).toFixed(1)} s @ ${opt.fps} fps)`);
}

async function main() {
  const opt = parseArgs(process.argv.slice(2));
  const chrome = process.env.CRAFTBOT_CHROME ?? CHROME_DEFAULT;
  // Both checked up front: a missing ffmpeg would otherwise surface minutes
  // later, with every frame already captured.
  if (!existsSync(chrome)) throw new Error(`Chrome not found at ${chrome} (set CRAFTBOT_CHROME)`);
  if (spawnSync("ffmpeg", ["-version"], { stdio: "ignore" }).status !== 0) {
    throw new Error("ffmpeg not found on PATH");
  }
  if (!existsSync(path.join(REPO, "viewer", "models", opt.model))) {
    throw new Error(`no such model: viewer/models/${opt.model}`);
  }
  await capture(opt, chrome);
  stitch(opt);
}

main().catch((err) => {
  console.error(`capture_knoll: ${err.message}`);
  process.exit(1);
});
