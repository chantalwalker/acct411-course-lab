# ================================================================
# COTTAGECORE PONG — Streamlit edition
#
# Controls:
#   W = up
#   S = down
#   Space = pause/resume
#
# Features:
#   • 1, 2, or 4 balls
#   • Adjustable ball speed
#   • Autoplay
#   • First to 7 points wins
#
# Python sets up the Streamlit page.
# HTML and CSS create the game's appearance.
# JavaScript handles controls, animation, collisions, and scoring.
# ================================================================

import streamlit as st

# Configure the browser tab and page layout.
st.set_page_config(
    page_title="Cottagecore Pong",
    page_icon="🌿",
    layout="wide",
)

# The r before the triple quotes creates a raw Python string.
# Everything between the triple quotes is the browser-based game.
game = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
  /* Cream, sage, dusty rose, and wood brown create the garden theme. */
  body {
    margin: 0;
    padding: 16px;
    background: #f7f0df;
    color: #4d6045;
    font-family: Georgia, serif;
    text-align: center;
  }

  .garden {
    max-width: 820px;
    margin: auto;
  }

  h1 {
    margin: 4px 0 8px;
    font-size: 28px;
  }

  p {
    margin: 8px 0;
    line-height: 1.5;
  }

  /* Settings wrap onto another line when the display is narrow. */
  .settings {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
    gap: 14px;
    padding: 12px;
    margin: 12px 0;
    background: #eee5d2;
    border-radius: 15px;
  }

  label {
    display: inline-flex;
    align-items: center;
    gap: 8px;
  }

  select, button {
    padding: 8px 14px;
    border: 1px solid #718563;
    border-radius: 16px;
    background: #dce6cf;
    color: #394b32;
    font: bold 15px Georgia, serif;
  }

  button {
    margin: 8px 4px;
    cursor: pointer;
  }

  button:hover {
    background: #cbdabb;
  }

  input[type="range"] {
    width: 145px;
    accent-color: #718563;
  }

  input[type="checkbox"] {
    width: 18px;
    height: 18px;
    accent-color: #718563;
    cursor: pointer;
  }

  output {
    min-width: 44px;
    font-weight: bold;
  }

  /* CSS scales the display; the game's coordinate system stays fixed. */
  canvas {
    display: block;
    width: 100%;
    height: auto;
    background: #e5ecd8;
    border: 5px solid #8b7658;
    border-radius: 18px;
    box-sizing: border-box;
    outline: none;
  }

  canvas:focus {
    border-color: #607853;
  }

  .hint {
    font-size: 14px;
  }
</style>
</head>

<body>
<div class="garden">
  <h1>🌿 Garden Pong 🌼</h1>
  <p>You tend the left paddle. The garden sprite tends the right.</p>

  <div class="settings">
    <label for="ballCount">
      Balls
      <select id="ballCount">
        <option value="1">1 ball</option>
        <option value="2">2 balls</option>
        <option value="4">4 balls</option>
      </select>
    </label>

    <label for="speed">
      Ball speed
      <input
        id="speed"
        type="range"
        min="0.5"
        max="2.5"
        step="0.1"
        value="1"
      >
      <output id="speedLabel" for="speed">1.0×</output>
    </label>

    <label for="autoplay">
      <input id="autoplay" type="checkbox">
      Autoplay
    </label>
  </div>

  <!-- tabindex lets the canvas receive keyboard input when focused. -->
  <canvas
    id="court"
    width="800"
    height="440"
    tabindex="0"
    aria-label="Pong. W moves up, S moves down, Space pauses."
  ></canvas>

  <div>
    <button id="start">Start / Resume</button>
    <button id="pause">Pause</button>
    <button id="restart">New Game</button>
  </div>

  <p id="status" role="status">Click Start / Resume to begin.</p>

  <p class="hint">
    Hold W: up · Hold S: down · Space: pause / resume · First to 7 wins
    <br>Ball count starts a new match. Speed changes apply immediately.
    <br>After adjusting a setting, click Start / Resume to use W and S.
  </p>
</div>

<script>
(() => {
  "use strict";

  // ==============================================================
  // 1. HTML ELEMENTS AND SETTINGS
  // ==============================================================

  const canvas = document.getElementById("court");
  const ctx = canvas.getContext("2d");
  const status = document.getElementById("status");
  const countSelect = document.getElementById("ballCount");
  const speedSlider = document.getElementById("speed");
  const speedLabel = document.getElementById("speedLabel");
  const autoplayCheckbox = document.getElementById("autoplay");

  // The internal canvas dimensions stay fixed even if CSS scales it.
  const WIDTH = canvas.width;
  const HEIGHT = canvas.height;

  // Leave room for flowers above and mushrooms below the court.
  const TOP = 48;
  const BOTTOM = HEIGHT - 38;

  const PW = 16; // Paddle width.
  const PH = 82; // Paddle height.

  // Movement speeds are measured in canvas pixels per second.
  const PLAYER_SPEED = 340;
  const COMPUTER_SPEED = 225;
  const START_SPEED = 300;
  const MAX_SPEED = 590;

  const WINNING_SCORE = 7;

  const colors = {
    green: "#718b62",
    rose: "#bd8290",
    brown: "#725c44",
    cream: "#fff9e9",
    line: "#b6c5a4"
  };

  // ==============================================================
  // 2. STATE — information that changes while the game runs
  // ==============================================================

  const player = { x: 30, y: 0, score: 0 };
  const computer = { x: WIDTH - 46, y: 0, score: 0 };

  // Track held keys so the paddle moves continuously.
  const keys = { w: false, s: false };

  // Each ball has its own position, velocity, color, and serve delay.
  let balls = [];
  let speedMultiplier = Number(speedSlider.value);
  let running = false;
  let finished = false;
  let previousTime = null;

  // Keep a number within a minimum and maximum.
  const clamp = (n, low, high) => Math.max(low, Math.min(high, n));

  function releaseKeys() {
    keys.w = false;
    keys.s = false;
  }

  // ==============================================================
  // 3. CREATE AND SERVE BALLS
  // ==============================================================

  function serve(ball, direction, delay = 0.8) {
    ball.x = WIDTH / 2;

    // Spread the balls vertically so they do not all overlap.
    const spacing = (BOTTOM - TOP) / (balls.length + 1);
    ball.y = TOP + spacing * (ball.id + 1);

    // Choose a slightly different angle for each serve.
    const angle = (Math.random() - 0.5) * 0.9;
    ball.vx = direction * START_SPEED * Math.cos(angle);
    ball.vy = START_SPEED * Math.sin(angle);
    ball.delay = delay;
  }

  function newGame() {
    running = false;
    finished = false;
    releaseKeys();

    player.score = computer.score = 0;
    player.y = computer.y = (TOP + BOTTOM - PH) / 2;

    const petalColors = [
      "#fff9e9",
      "#e8b8c6",
      "#c4d8ed",
      "#e9ce94"
    ];

    // Create exactly as many balls as the user selected.
    balls = Array.from(
      { length: Number(countSelect.value) },
      (_, id) => ({
        id,
        x: 0,
        y: 0,
        vx: 0,
        vy: 0,
        radius: 8,
        delay: 0,
        color: petalColors[id]
      })
    );

    // Alternate directions and stagger the initial serves.
    balls.forEach((ball, index) => {
      serve(ball, index % 2 === 0 ? -1 : 1, 0.8 + index * 0.25);
    });

    status.textContent = "Click Start / Resume to begin.";
  }

  function startGame() {
    if (finished) newGame();

    running = true;

    // Keyboard controls work when the canvas has focus.
    canvas.focus();

    status.textContent = "Use W and S (or Autoplay). First to 7 wins!";
  }

  function pauseGame() {
    if (!running) return;

    running = false;
    releaseKeys();

    status.textContent = "Paused. Click Start / Resume to continue.";
  }

  // ==============================================================
  // 4. SETTINGS AND INPUT
  // ==============================================================

  countSelect.addEventListener("change", () => {
    // A different ball count starts a fresh match.
    newGame();
    status.textContent = "Ball count updated. Click Start / Resume.";
  });

  speedSlider.addEventListener("input", () => {
    // Store the multiplier separately from each ball's base velocity.
    // This prevents repeated slider changes from distorting speeds.
    speedMultiplier = Number(speedSlider.value);
    speedLabel.textContent = speedMultiplier.toFixed(1) + "×";
  });

  canvas.addEventListener("keydown", (event) => {
    const key = event.key.toLowerCase();

    if (key === "w" || key === "s") {
      event.preventDefault();
      keys[key] = true;
    }

    if (event.code === "Space") {
      event.preventDefault();

      // Holding Space should not repeatedly toggle pause.
      if (!event.repeat) {
        if (running) pauseGame();
        else startGame();
      }
    }
  });

  canvas.addEventListener("keyup", (event) => {
    const key = event.key.toLowerCase();

    if (key === "w" || key === "s") {
      event.preventDefault();
      keys[key] = false;
    }
  });

  canvas.addEventListener("pointerdown", () => canvas.focus());

  // Pause when focus moves away from the game.
  // Clearing held keys prevents the paddle from getting stuck moving.
  canvas.addEventListener("blur", pauseGame);
  window.addEventListener("blur", pauseGame);

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) pauseGame();
  });

  document.getElementById("start").onclick = startGame;
  document.getElementById("pause").onclick = pauseGame;

  document.getElementById("restart").onclick = () => {
    newGame();
    startGame();
  };

  // ==============================================================
  // 5. COLLISIONS AND SCORING
  // ==============================================================

  function bounceOff(ball, paddle, direction) {
    const center = paddle.y + PH / 2;

    // Center hits bounce gently; edge hits produce steeper angles.
    const hit = clamp((ball.y - center) / (PH / 2), -1, 1);
    const angle = hit * Math.PI / 3;

    // Increase speed a little after each hit, up to MAX_SPEED.
    const speed = Math.min(
      Math.hypot(ball.vx, ball.vy) * 1.045,
      MAX_SPEED
    );

    ball.vx = direction * speed * Math.cos(angle);
    ball.vy = speed * Math.sin(angle);

    // Push the ball outside the paddle to avoid duplicate collisions.
    ball.x = direction > 0
      ? paddle.x + PW + ball.radius
      : paddle.x - ball.radius;
  }

  function awardPoint(scorer, ball, direction) {
    scorer.score++;

    if (scorer.score >= WINNING_SCORE) {
      finished = true;
      running = false;
      releaseKeys();

      status.textContent = scorer === player
        ? "🌼 You won! Click New Game for another garden match."
        : "🌿 The garden sprite won! Click New Game to try again.";
    } else {
      // Only reset the ball that went out. Others keep playing.
      serve(ball, direction);
    }
  }

  function updateBall(ball, dt) {
    if (ball.delay > 0) {
      // Serve delays use seconds and are independent of ball speed.
      ball.delay = Math.max(0, ball.delay - dt);
      return;
    }

    const oldX = ball.x;

    // The slider changes ball movement, but not paddle movement.
    ball.x += ball.vx * speedMultiplier * dt;
    ball.y += ball.vy * speedMultiplier * dt;

    // Bounce off the upper edge.
    if (ball.y - ball.radius < TOP) {
      ball.y = TOP + ball.radius;
      ball.vy = Math.abs(ball.vy);
    }

    // Bounce off the lower edge.
    if (ball.y + ball.radius > BOTTOM) {
      ball.y = BOTTOM - ball.radius;
      ball.vy = -Math.abs(ball.vy);
    }

    // Check whether the ball overlaps a paddle vertically.
    const overlaps = (paddle) =>
      ball.y + ball.radius >= paddle.y &&
      ball.y - ball.radius <= paddle.y + PH;

    // Detect a left-moving ball crossing the player's paddle face.
    const leftFace = player.x + PW + ball.radius;

    if (
      ball.vx < 0 &&
      oldX >= leftFace &&
      ball.x <= leftFace &&
      overlaps(player)
    ) {
      bounceOff(ball, player, 1);
    }

    // Detect a right-moving ball crossing the computer's paddle face.
    const rightFace = computer.x - ball.radius;

    if (
      ball.vx > 0 &&
      oldX <= rightFace &&
      ball.x >= rightFace &&
      overlaps(computer)
    ) {
      bounceOff(ball, computer, -1);
    }

    // Award a point when the entire ball leaves the canvas.
    if (ball.x + ball.radius < 0) {
      awardPoint(computer, ball, -1);
    } else if (ball.x - ball.radius > WIDTH) {
      awardPoint(player, ball, 1);
    }
  }

  function update(dt) {
    // --- Player paddle: manual control or Autoplay ---
    if (autoplayCheckbox.checked) {
      // Find the incoming ball expected to arrive soonest.
      let threat = null;
      let earliestArrival = Infinity;

      for (const ball of balls) {
        if (ball.vx >= 0 || ball.delay > 0) continue;

        const arrival =
          (ball.x - player.x) / (-ball.vx * speedMultiplier);

        if (arrival >= 0 && arrival < earliestArrival) {
          earliestArrival = arrival;
          threat = ball;
        }
      }

      const targetY = threat ? threat.y : (TOP + BOTTOM) / 2;
      const difference = targetY - (player.y + PH / 2);

      player.y = clamp(
        player.y + clamp(
          difference,
          -PLAYER_SPEED * dt,
          PLAYER_SPEED * dt
        ),
        TOP,
        BOTTOM - PH
      );
    } else {
      // S moves down; W moves up. Holding both cancels movement.
      const movement = (keys.s ? 1 : 0) - (keys.w ? 1 : 0);

      player.y = clamp(
        player.y + movement * PLAYER_SPEED * dt,
        TOP,
        BOTTOM - PH
      );
    }

    // --- Computer paddle control ---
    let threat = null;
    let earliestArrival = Infinity;

    for (const ball of balls) {
      if (ball.vx <= 0 || ball.delay > 0) continue;

      const arrival =
        (computer.x - ball.x) / (ball.vx * speedMultiplier);

      if (arrival >= 0 && arrival < earliestArrival) {
        earliestArrival = arrival;
        threat = ball;
      }
    }

    const targetY = threat ? threat.y : (TOP + BOTTOM) / 2;
    const difference = targetY - (computer.y + PH / 2);

    computer.y = clamp(
      computer.y + clamp(
        difference,
        -COMPUTER_SPEED * dt,
        COMPUTER_SPEED * dt
      ),
      TOP,
      BOTTOM - PH
    );

    // Stop immediately after a winning point.
    for (const ball of balls) {
      if (!running) break;
      updateBall(ball, dt);
    }
  }

  // ==============================================================
  // 6. DRAWING — flowers, mushrooms, paddles, balls, and scores
  // ==============================================================

  function circle(x, y, radius, color) {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();
  }

  function flower(x, y, color) {
    // Draw five petals around a golden center.
    for (let petal = 0; petal < 5; petal++) {
      const angle = petal * Math.PI * 2 / 5;

      circle(
        x + Math.cos(angle) * 5,
        y + Math.sin(angle) * 5,
        4,
        color
      );
    }

    circle(x, y, 3, "#d5ab58");
  }

  function mushroom(x, y) {
    // Stem.
    ctx.fillStyle = colors.cream;
    ctx.fillRect(x - 3, y, 6, 12);

    // Cap.
    ctx.fillStyle = colors.rose;
    ctx.beginPath();
    ctx.arc(x, y, 12, Math.PI, 0);
    ctx.fill();

    // Spots.
    circle(x - 5, y - 5, 2, colors.cream);
    circle(x + 4, y - 7, 2, colors.cream);
  }

  function drawPaddle(paddle, color) {
    ctx.fillStyle = color;
    ctx.fillRect(paddle.x, paddle.y, PW, PH);

    // A pale highlight adds a little texture.
    ctx.strokeStyle = "#ffffff66";
    ctx.beginPath();
    ctx.moveTo(paddle.x + 5, paddle.y + 8);
    ctx.lineTo(paddle.x + 5, paddle.y + PH - 8);
    ctx.stroke();
  }

  function draw() {
    // Paint over the previous frame.
    ctx.fillStyle = "#e5ecd8";
    ctx.fillRect(0, 0, WIDTH, HEIGHT);

    // Decorative flowers above the court.
    for (let x = 22; x < WIDTH; x += 42) {
      flower(
        x,
        20,
        x % 84 === 22 ? colors.cream : "#e3b7bc"
      );
    }

    // Decorative mushrooms below the court.
    for (let x = 28; x < WIDTH; x += 90) {
      mushroom(x, HEIGHT - 17);
    }

    // Court outline.
    ctx.strokeStyle = colors.line;
    ctx.lineWidth = 2;
    ctx.strokeRect(12, TOP, WIDTH - 24, BOTTOM - TOP);

    // Dashed center line.
    ctx.setLineDash([5, 12]);
    ctx.beginPath();
    ctx.moveTo(WIDTH / 2, TOP);
    ctx.lineTo(WIDTH / 2, BOTTOM);
    ctx.stroke();
    ctx.setLineDash([]);

    // Scores.
    ctx.fillStyle = colors.brown;
    ctx.font = "bold 30px Georgia";
    ctx.textAlign = "center";
    ctx.fillText(player.score, WIDTH / 2 - 65, TOP + 37);
    ctx.fillText(computer.score, WIDTH / 2 + 65, TOP + 37);

    drawPaddle(player, colors.green);
    drawPaddle(computer, colors.rose);

    for (const ball of balls) {
      // Waiting balls are faint so upcoming serves are easy to spot.
      ctx.globalAlpha = ball.delay > 0 ? 0.35 : 1;
      flower(ball.x, ball.y, ball.color);
    }

    // Restore opacity before drawing other objects.
    ctx.globalAlpha = 1;

    // Display an overlay when paused or after the match ends.
    if (!running) {
      ctx.fillStyle = "#f7f0dfeb";
      ctx.fillRect(155, 170, 490, 100);

      ctx.fillStyle = colors.brown;
      ctx.font = "bold 25px Georgia";
      ctx.fillText(
        finished ? "A lovely match!" : "A little garden break",
        WIDTH / 2,
        211
      );

      ctx.font = "17px Georgia";
      ctx.fillText(
        finished ? "Click New Game to play again" : "Click Start / Resume",
        WIDTH / 2,
        243
      );
    }
  }

  // ==============================================================
  // 7. ANIMATION LOOP
  // ==============================================================

  function animate(timestamp) {
    if (previousTime === null) previousTime = timestamp;

    // Convert milliseconds to seconds.
    // Cap long frames to prevent jumps after browser interruptions.
    const dt = Math.min((timestamp - previousTime) / 1000, 0.04);
    previousTime = timestamp;

    if (running) {
      // Small physics steps help fast balls collide reliably.
      const steps = Math.max(1, Math.ceil(dt / (1 / 240)));

      for (let i = 0; i < steps && running; i++) {
        update(dt / steps);
      }
    }

    draw();

    // Ask the browser to run this function again next frame.
    requestAnimationFrame(animate);
  }

  // Prepare the first match and start the animation loop.
  newGame();
  requestAnimationFrame(animate);
})();
</script>
</body>
</html>
"""

# Embed the game in the Streamlit page.
# The iframe keeps the game's styles and keyboard events contained.
# JavaScript runs inside the iframe to make the game interactive.
st.iframe(game, height=850)
