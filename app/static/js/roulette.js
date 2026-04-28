/**
 * app/static/js/roulette.js
 * 晚餐輪盤前端邏輯：繪製 Canvas、動畫旋轉、API 互動
 */

const canvas = document.getElementById('wheel');
const ctx = canvas ? canvas.getContext('2d') : null;
const spinBtn = document.getElementById('spin-btn');
const resultDisplay = document.getElementById('result-display');
const winnerNameElem = document.getElementById('winner-name');

let currentAngle = 0;
let isSpinning = false;

// 預定義顏色庫
const colors = [
    '#6c5ce7', '#a29bfe', '#ff7675', '#fab1a0', 
    '#55efc4', '#81ecec', '#ffeaa7', '#fdcb6e',
    '#0984e3', '#74b9ff', '#e84393', '#fd79a8'
];

/**
 * 初始化並繪製輪盤
 */
function drawWheel() {
    if (!ctx || !rouletteData.length) return;

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = canvas.width / 2 - 10;

    const totalWeight = rouletteData.reduce((sum, item) => sum + item.weight, 0);
    let startAngle = currentAngle;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    rouletteData.forEach((item, index) => {
        const sliceAngle = (item.weight / totalWeight) * 2 * Math.PI;

        // 畫扇形
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle);
        ctx.closePath();
        ctx.fillStyle = colors[index % colors.length];
        ctx.fill();
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.stroke();

        // 寫文字
        ctx.save();
        ctx.translate(centerX, centerY);
        ctx.rotate(startAngle + sliceAngle / 2);
        ctx.textAlign = "right";
        ctx.fillStyle = "#fff";
        ctx.font = "bold 18px 'Outfit', sans-serif";
        ctx.fillText(item.name, radius - 30, 10);
        ctx.restore();

        startAngle += sliceAngle;
    });

    // 畫中心圓
    ctx.beginPath();
    ctx.arc(centerX, centerY, 30, 0, 2 * Math.PI);
    ctx.fillStyle = "#fff";
    ctx.fill();
    ctx.strokeStyle = colors[0];
    ctx.lineWidth = 5;
    ctx.stroke();
}

/**
 * 執行旋轉動畫
 */
async function spin() {
    if (isSpinning || !rouletteData.length) return;
    
    isSpinning = true;
    spinBtn.disabled = true;
    resultDisplay.classList.remove('show');

    try {
        // 1. 同步向後端請求結果
        const response = await fetch('/roll', { method: 'POST' });
        const data = await response.json();

        if (!response.ok) throw new Error(data.error || '抽籤失敗');

        // 2. 計算目標角度
        const winnerIndex = rouletteData.findIndex(item => item.id === data.id);
        const totalWeight = rouletteData.reduce((sum, item) => sum + item.weight, 0);
        
        // 計算各品項的角度間隔
        let accumulatedWeight = 0;
        const winnerStartWeight = rouletteData.slice(0, winnerIndex).reduce((sum, i) => sum + i.weight, 0);
        const winnerEndWeight = winnerStartWeight + rouletteData[winnerIndex].weight;
        
        const winnerStartAngle = (winnerStartWeight / totalWeight) * 2 * Math.PI;
        const winnerEndAngle = (winnerEndWeight / totalWeight) * 2 * Math.PI;
        const targetSliceAngle = (winnerStartAngle + winnerEndAngle) / 2;

        // 為了讓指針指到目標，我們需要：
        // 目前角度 + 多轉幾圈 (例如 5 圈) - 目標角度的偏移量
        // 註：Canvas 0度是在 3 點鐘方向，指針是在 12 點鐘方向 (1.5 PI)
        const extraSpins = 5 * 2 * Math.PI;
        const pointerOffset = 1.5 * Math.PI;
        const finalTargetAngle = currentAngle + extraSpins + (pointerOffset - targetSliceAngle - currentAngle % (2 * Math.PI));

        // 3. 執行動畫
        animateRotation(finalTargetAngle, data.name);

    } catch (err) {
        alert(err.message);
        isSpinning = false;
        spinBtn.disabled = false;
    }
}

function animateRotation(targetAngle, winnerName) {
    const startTime = performance.now();
    const duration = 4000; // 4 秒
    const startAngle = currentAngle;

    function frame(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // 使用 easeOut 工程曲線
        const easeOut = 1 - Math.pow(1 - progress, 3);
        currentAngle = startAngle + (targetAngle - startAngle) * easeOut;

        drawWheel();

        if (progress < 1) {
            requestAnimationFrame(frame);
        } else {
            isSpinning = false;
            spinBtn.disabled = false;
            showResult(winnerName);
        }
    }
    requestAnimationFrame(frame);
}

function showResult(name) {
    winnerNameElem.innerText = name;
    resultDisplay.classList.add('show');
    
    // 噴灑碎花效果 (如果以後有庫的話)
    console.log('抽中：', name);
}

function resetRoulette() {
    resultDisplay.classList.remove('show');
    spin();
}

// 初始化
if (canvas) {
    drawWheel();
    spinBtn.addEventListener('click', spin);
}
