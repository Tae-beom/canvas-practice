import streamlit as st
import streamlit.components.v1 as components

html_code = """
<!-- ▼ 큰 드롭다운 UI: 캔버스 위, 가운데 정렬 -->
<div style="width:700px;margin:8px auto 10px auto;display:flex;justify-content:center;position:relative;">
  <!-- 선택 박스 -->
  <select id="modeSelect"
    style="
      width: 360px;
      height: 54px;
      font-family: Arial;
      font-size: 28px;
      font-weight: 800;
      text-align: center;
      color: #111;
      background: #fff;
      border: 2px solid #2a4a7f;
      border-radius: 10px;
      box-shadow: 0 3px 10px rgba(0,0,0,0.08);
      padding: 0 64px 0 24px;   /* 우측에 ▼ 공간 */
      appearance: none;         /* 기본 화살표 제거 (브라우저별) */
      -webkit-appearance: none;
      -moz-appearance: none;
      outline: none;
      cursor: pointer;
    ">
    <option value="평상시" selected>평상시</option>
    <option value="엘니뇨">엘니뇨</option>
    <option value="라니냐">라니냐</option>
  </select>

  <!-- 오른쪽 파란 ▼ 아이콘 (select 위에 겹쳐 배치) -->
  <div style="
      position:absolute;
      right: calc( (700px - 360px) / 2 + 16px );  /* 컨테이너 우측 여백 + 삼각형 여백 */
      top: 50%;
      transform: translateY(-50%);
      width: 0; height: 0;
      border-left: 14px solid transparent;
      border-right: 14px solid transparent;
      border-top: 20px solid #3a66b7;  /* 파란 삼각형 */
      pointer-events: none;            /* 클릭 방해 X */
    ">
  </div>
</div>

<canvas id="myCanvas" width="700" height="450" style="border:1px solid #ccc;"></canvas>

<script>
const canvas = document.getElementById("myCanvas");
const ctx = canvas.getContext("2d");

/* ========== 모드 상태 (추후 동작 분기용) ========== */
let currentMode = "평상시";
document.getElementById("modeSelect").addEventListener("change", (e) => {
  currentMode = e.target.value;
  // 필요 시: currentMode 값으로 thermocline/용승/띠 색 등 변경 가능
});

/* =========================
   공용 화살표 그리기 함수
   ========================= */
function drawArrow(fromX, fromY, toX, toY, color) {
  const headLength = 10;
  const dx = toX - fromX;
  const dy = toY - fromY;
  const angle = Math.atan2(dy, dx);

  ctx.beginPath();
  ctx.moveTo(fromX, fromY);
  ctx.lineTo(toX, toY);
  ctx.strokeStyle = color;
  ctx.lineWidth = 3;
  ctx.stroke();

  ctx.beginPath();
  ctx.moveTo(toX, toY);
  ctx.lineTo(
    toX - headLength * Math.cos(angle - Math.PI / 6),
    toY - headLength * Math.sin(angle - Math.PI / 6)
  );
  ctx.lineTo(
    toX - headLength * Math.cos(angle + Math.PI / 6),
    toY - headLength * Math.sin(angle + Math.PI / 6)
  );
  ctx.lineTo(toX, toY);
  ctx.fillStyle = color;
  ctx.fill();
}

/* =========================
   일정 길이 화살표(중심+방향)
   ========================= */
function drawArrowCentered(cx, cy, dirX, dirY, totalLen, color) {
  const len = Math.hypot(dirX, dirY) || 1;
  const ux = dirX / len, uy = dirY / len;

  const headLen = 12;                 // 화살촉 길이
  const tailLen = totalLen - headLen; // 몸통+꼬리

  // 꼬리/몸통 비율
  const fromX = cx - ux * tailLen * 0.6;
  const fromY = cy - uy * tailLen * 0.6;
  const toX   = cx + ux * tailLen * 0.4;
  const toY   = cy + uy * tailLen * 0.4;

  drawArrow(fromX, fromY, toX, toY, color);
}

/* =========================
   구름 + 비(애니메이션 파티클)
   ========================= */
function drawCloud(x, y, bob=0) {
  ctx.fillStyle = "#eeeeee"; // 밝은 회색 구름

  // 윗부분
  ctx.beginPath();
  ctx.arc(x, y + bob, 15, 0, Math.PI * 2);
  ctx.arc(x + 20, y + bob, 20, 0, Math.PI * 2);
  ctx.arc(x - 20, y + bob, 20, 0, Math.PI * 2);
  ctx.arc(x, y - 10 + bob, 20, 0, Math.PI * 2);
  ctx.fill();

  // 아랫부분(몽실몽실 추가)
  ctx.beginPath();
  ctx.arc(x - 15, y + 15 + bob, 18, 0, Math.PI * 2);
  ctx.arc(x + 15, y + 15 + bob, 18, 0, Math.PI * 2);
  ctx.arc(x, y + 18 + bob, 20, 0, Math.PI * 2);
  ctx.fill();
}

const RAIN_COUNT = 20;
let rainDrops = [];
function initRain() {
  rainDrops = [];
  for (let i=0; i<RAIN_COUNT; i++) {
    rainDrops.push({
      x: 80 + Math.random()*40,     // x≈100 주변
      y: 58 + Math.random()*40,     // 구름 아래
      vx: -0.6,                     // 약간 왼쪽 기울기
      vy: 2 + Math.random()*1.5,    // 낙하 속도
      len: 14 + Math.random()*8     // 빗줄기 길이
    });
  }
}
function updateAndDrawRain() {
  ctx.strokeStyle = "rgba(30,100,255,0.55)";
  ctx.lineWidth = 2;
  for (let d of rainDrops) {
    ctx.beginPath();
    ctx.moveTo(d.x, d.y);
    ctx.lineTo(d.x + d.vx*6, d.y + d.len);
    ctx.stroke();
    d.x += d.vx;
    d.y += d.vy;
    if (d.y > 138) { // 해수면 근처에서 재생성
      d.x = 80 + Math.random()*40;
      d.y = 58 + Math.random()*15;
      d.vx = -0.6;
      d.vy = 2 + Math.random()*1.5;
      d.len = 14 + Math.random()*8;
    }
  }
}

/* =========================
   정적 레이어(배경, 라벨 등)
   ========================= */
function drawBase(){
  // 바다 배경
  ctx.fillStyle = "#cceeff";
  ctx.fillRect(0, 150, 700, 250);

  // 수온 편차 띠 (가운데 옅은 회색 두껍게)
  let grad = ctx.createLinearGradient(0, 140, 700, 140);
  grad.addColorStop(0, "red");
  grad.addColorStop(0.4, "#f5f5f5");
  grad.addColorStop(0.6, "#f5f5f5");
  grad.addColorStop(1, "blue");
  ctx.fillStyle = grad;
  ctx.fillRect(0, 140, 700, 10);

  // 수온편차 텍스트
  ctx.font = "14px Arial";
  ctx.fillStyle = "black";
  ctx.textAlign = "center";
  ctx.fillText("수온편차", 350, 130);

  // Thermocline (수온약층)
  ctx.beginPath();
  ctx.moveTo(0, 300);
  ctx.lineTo(700, 200);
  ctx.strokeStyle = "#003366";
  ctx.lineWidth = 3;
  ctx.stroke();

  // 수온약층 라벨(선과 같은 기울기)
  ctx.save();
  ctx.translate(350, 250);
  ctx.rotate(Math.atan2(-100, 700));
  ctx.font = "14px Arial";
  ctx.fillStyle = "black";
  ctx.textAlign = "center";
  ctx.fillText("수온약층", 0, -5);
  ctx.restore();

  // 용승(동쪽 연안, 수직 들어올림)
  drawArrow(660, 260, 660, 210, "green");
  ctx.font = "14px Arial";
  ctx.fillStyle = "black";
  ctx.textAlign = "center";
  ctx.fillText("용승", 660, 280);

  // 범례 (작은 그라데이션: 빨강 - 밝은회색 - 파랑)
  let legendGrad = ctx.createLinearGradient(620, 360, 680, 360);
  legendGrad.addColorStop(0, "red");
  legendGrad.addColorStop(0.5, "#f5f5f5");
  legendGrad.addColorStop(1, "blue");
  ctx.fillStyle = legendGrad;
  ctx.fillRect(620, 360, 60, 10);
  ctx.fillStyle = "black";
  ctx.font = "13px Arial";
  ctx.textAlign = "center";
  ctx.fillText("+", 620, 355);
  ctx.fillText("-", 680, 355);
  ctx.fillText("수온 편차", 650, 385);

  // 경도 라벨
  ctx.font = "12px Arial";
  ctx.textAlign = "center";
  ctx.fillStyle = "black";
  let longitudes = ["120°E", "150°E", "180°", "150°W", "120°W"];
  for (let i = 0; i < 5; i++) {
    ctx.fillText(longitudes[i], 80 + i * 140, 410);
  }
}

/* =========================
   워커 순환 애니메이션
   ========================= */
let walkerT = 0;
const walkerStep = 2;           // 프레임당 진행량 (속도 미세조절)
const cycle = 700;              // 한 바퀴 도는 프레임 수
let arrowColor = "#808080";     // 회색 바람 화살표
const arrowLenPx = 64;          // 화살표 길이(px)

initRain(); // 빗방울 초기화

function animateWalker() {
  // 전체 지우기 → 잔상 제거
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // 정적 레이어
  drawBase();

  // 서태평양 상승부 구름 + 비 (구름은 살짝 흔들림)
  const cloudBob = Math.sin(walkerT * 0.06) * 2;
  drawCloud(95, 45, cloudBob);
  updateAndDrawRain();

  // 워커 순환 경로(수온편차 글씨 y=130보다 항상 위쪽)
  const points = [
    { x: 100, y: 70 },   // 서태평양 상승 시작
    { x: 100, y: 30 },   // 상층
    { x: 600, y: 30 },   // 상층 서→동
    { x: 600, y: 70 },   // 동태평양 하강 상단
    { x: 600, y: 110 },  // 하강 중간
    { x: 600, y: 115 },  // 표면 도달
    { x: 100, y: 115 },  // 표면 동→서(글씨 위)
    { x: 100, y: 110 }    // 상승 전환
  ];

  // 총 길이 계산
  let totalLength = 0;
  const segmentLengths = [];
  for (let i = 0; i < points.length; i++) {
    const p1 = points[i];
    const p2 = points[(i + 1) % points.length];
    const len = Math.hypot(p2.x - p1.x, p2.y - p1.y);
    segmentLengths.push(len);
    totalLength += len;
  }

  // 동시에 4개의 화살표가 순차 회전
  const phase = (walkerT % cycle) / cycle;
  for (let n = 0; n < 4; n++) {
    let distance = ((phase + n / 4) % 1.0) * totalLength;

    let segment = 0;
    while (distance > segmentLengths[segment]) {
      distance -= segmentLengths[segment];
      segment++;
    }
    const p1 = points[segment];
    const p2 = points[(segment + 1) % points.length];

    const segLen = segmentLengths[segment] || 1;
    const ratio = distance / segLen;

    const cx = p1.x + (p2.x - p1.x) * ratio;
    const cy = p1.y + (p2.y - p1.y) * ratio;

    drawArrowCentered(cx, cy, p2.x - p1.x, p2.y - p1.y, arrowLenPx, arrowColor);
  }

  walkerT += walkerStep;
  requestAnimationFrame(animateWalker);
}

animateWalker();
</script>
"""

components.html(html_code, height=500)
