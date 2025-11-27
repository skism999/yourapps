// API base URL
const API_BASE = '';  // 同じオリジンの場合は空文字

// ページロード時にセレクトボックスの選択肢を生成
document.addEventListener('DOMContentLoaded', () => {
    initializeDateTimeSelects();
});

// 年月日時分のセレクトボックスを初期化
function initializeDateTimeSelects() {
    const yearSelect = document.getElementById('birth-year');
    const monthSelect = document.getElementById('birth-month');
    const daySelect = document.getElementById('birth-day');
    const hourSelect = document.getElementById('birth-hour');
    const minuteSelect = document.getElementById('birth-minute');

    if (!yearSelect) return; // 入力画面でない場合は処理しない

    // 年の選択肢を生成（1900年〜現在年）
    const currentYear = new Date().getFullYear();
    for (let year = currentYear; year >= 1900; year--) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year + '年';
        yearSelect.appendChild(option);
    }

    // 月の選択肢を生成（1〜12月）
    for (let month = 1; month <= 12; month++) {
        const option = document.createElement('option');
        option.value = month;
        option.textContent = month + '月';
        monthSelect.appendChild(option);
    }

    // 日の選択肢を生成（1〜31日）
    for (let day = 1; day <= 31; day++) {
        const option = document.createElement('option');
        option.value = day;
        option.textContent = day + '日';
        daySelect.appendChild(option);
    }

    // 時の選択肢を生成（0〜23時）
    for (let hour = 0; hour <= 23; hour++) {
        const option = document.createElement('option');
        option.value = hour;
        option.textContent = hour + '時';
        hourSelect.appendChild(option);
    }

    // 分の選択肢を生成（0〜59分）
    for (let minute = 0; minute <= 59; minute++) {
        const option = document.createElement('option');
        option.value = minute;
        option.textContent = minute + '分';
        minuteSelect.appendChild(option);
    }
}

// 入力フォームの処理
document.getElementById('input-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('name').value.trim();

    // セレクトボックスから値を取得
    const year = document.getElementById('birth-year').value;
    const month = document.getElementById('birth-month').value;
    const day = document.getElementById('birth-day').value;
    const hour = document.getElementById('birth-hour').value;
    const minute = document.getElementById('birth-minute').value;

    // 生年月日をYYYY-MM-DD形式に変換
    const birthdate = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    // 時刻をHH:MM形式に変換
    const birthtime = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;

    // ローディング表示
    showLoading();
    hideError();

    try {
        // 診断結果を生成
        const response = await fetch(`${API_BASE}/api/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name || null,
                birthdate: birthdate,
                birthtime: birthtime
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '結果の生成に失敗しました');
        }

        const resultData = await response.json();

        // 結果をセッションストレージに保存
        sessionStorage.setItem('result', JSON.stringify(resultData));

        // 結果ページに遷移
        window.location.href = '/static/result.html';

    } catch (error) {
        console.error('Error:', error);
        // エラーメッセージを正しく表示
        const errorMessage = error.message || error.toString() || '結果の生成に失敗しました';
        showError(errorMessage);
    } finally {
        hideLoading();
    }
});

// 結果表示処理
function displayResult() {
    const resultData = JSON.parse(sessionStorage.getItem('result'));

    if (!resultData) {
        console.error('結果データが見つかりません');
        window.location.href = '/';
        return;
    }

    console.log('Result data:', resultData);

    // 画像表示
    displayResultImage(resultData);

    // 取得した数字を表示
    displayNumbers(resultData);

    // 必殺技とアイテムの名前一覧を表示
    displayNamesList(resultData);

    // 色ごとの枚数を表示
    displayColorCounts(resultData);

    // 必殺技の説明を表示
    displayHissatsuwaza(resultData);

    // アイテムの説明を表示
    displayItems(resultData);

    // 動き方の説明を表示
    displayActions(resultData);
}

// 画像表示
function displayResultImage(data) {
    const resultImage = document.getElementById('result-image');
    if (resultImage && data.image_url) {
        resultImage.src = data.image_url;
        resultImage.onerror = () => {
            console.error('画像の読み込みに失敗しました');
            resultImage.alt = '画像の読み込みに失敗しました';
        };
    }
}

// 取得した数字を表示
function displayNumbers(data) {
    const container = document.getElementById('numbers-container');
    if (!container) return;

    const hissatsuNumbers = new Set(data.hissatsu_numbers || []);

    container.innerHTML = data.numbers.map(num => {
        const isHissatsu = hissatsuNumbers.has(num);
        const colorClass = isHissatsu ? 'bg-gradient-to-br from-red-500 to-red-600 text-white shadow-lg' : 'bg-gradient-to-br from-gray-200 to-gray-300 text-gray-800';
        return `<span class="${colorClass} px-6 py-3 rounded-xl font-bold text-lg transition-all duration-300 hover:scale-110 hover:shadow-xl">${num}</span>`;
    }).join('');
}

// 必殺技とアイテムの名前一覧を表示
function displayNamesList(data) {
    const container = document.getElementById('names-list');
    if (!container) return;

    const names = [];

    // 必殺技名を追加
    if (data.hissatsus && data.hissatsus.length > 0) {
        data.hissatsus.forEach(h => {
            names.push(`<div class="text-gray-800 font-bold text-base md:text-lg py-2">【必殺技】 ${h.name}</div>`);
        });
    }

    // アイテム名を追加
    if (data.items && data.items.length > 0) {
        data.items.forEach(item => {
            names.push(`<div class="text-gray-700 text-sm md:text-base py-1.5">No.${item.no}  ${item.name}</div>`);
        });
    }

    container.innerHTML = names.join('');
}

// 色ごとの枚数を表示
function displayColorCounts(data) {
    const container = document.getElementById('color-counts-container');
    if (!container || !data.color_counts) return;

    const colorSystems = data.color_counts.color_systems || [];

    container.innerHTML = colorSystems.map(system => {
        const colorsHtml = system.colors.map(color => `
            <div class="ml-4 md:ml-8 text-gray-700 py-2">
                <span class="font-semibold text-sm md:text-base">${color.name}:</span>
                <span class="ml-1 md:ml-2 text-sm md:text-base">${color.meaning}</span>
                <span class="ml-2 md:ml-3 text-lg md:text-xl font-bold text-purple-600">${color.count}枚</span>
            </div>
        `).join('');

        return `
            <div class="border-l-4 border-purple-500 pl-4 md:pl-6 py-4 bg-gradient-to-r from-purple-50 to-transparent rounded-r-lg color-system-card">
                <div class="font-bold text-lg md:text-xl text-gray-800">
                    ${system.name}: ${system.meaning}
                    <span class="block md:inline mt-2 md:mt-0 md:ml-3 text-xl md:text-2xl text-purple-600">${system.total_count}枚</span>
                </div>
                <div class="mt-4 space-y-2">
                    ${colorsHtml}
                </div>
            </div>
        `;
    }).join('');
}

// 必殺技の説明を表示
function displayHissatsuwaza(data) {
    const section = document.getElementById('hissatsuwaza-section');
    const container = document.getElementById('hissatsuwaza-container');

    if (!container || !data.hissatsus || data.hissatsus.length === 0) {
        section?.classList.add('hidden');
        return;
    }

    section?.classList.remove('hidden');

    container.innerHTML = data.hissatsus.map(h => `
        <div class="pl-4 md:pl-8 py-6 bg-gradient-to-r from-red-50 to-transparent rounded-r-xl hover:shadow-lg transition-shadow duration-300">
            ${h.image_url ? `<div class="mb-6"><img src="${h.image_url}" alt="${h.name}" class="w-full max-w-md md:max-w-lg h-auto object-contain rounded-lg shadow-md mx-auto hissatsu-image-mobile"></div>` : ''}
            <div>
                <h3 class="text-xl md:text-2xl font-bold text-gray-800 mb-4 md:mb-6">
                    ${h.name}
                </h3>
                <div class="space-y-3 text-gray-700 text-sm md:text-base leading-relaxed">
                    <div><span class="font-semibold">色:</span> <span class="ml-2">${h.color}</span></div>
                    <div><span class="font-semibold">意味:</span> <span class="ml-2">${h.meaning}</span></div>
                    <div><span class="font-semibold">動き方:</span> <span class="ml-2">${h.movement}</span></div>
                    <div><span class="font-semibold">基本姿勢:</span> <span class="ml-2">${h.basic_posture}</span></div>
                    <div><span class="font-semibold">才能:</span> <span class="ml-2">${h.talent}</span></div>
                    <div><span class="font-semibold">特性:</span> <span class="ml-2">${h.characteristics}</span></div>
                    <div class="pt-2"><span class="font-semibold text-blue-600">アドバイス:</span> <span class="ml-2">${h.advice}</span></div>
                    <div class="mt-4 md:mt-6 pt-4 md:pt-6 border-t-2 border-red-200 space-y-2">
                        <div class="text-green-600 font-medium text-sm md:text-base"><span class="font-bold">ON:</span> <span class="ml-2">${h.on_state}</span></div>
                        <div class="text-red-600 font-medium text-sm md:text-base"><span class="font-bold">OFF:</span> <span class="ml-2">${h.off_state}</span></div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// アイテムの説明を表示
function displayItems(data) {
    const container = document.getElementById('items-container');
    if (!container || !data.items) return;

    container.innerHTML = data.items.map(item => `
        <div class="pl-4 md:pl-8 py-6 bg-gradient-to-r from-blue-50 to-transparent rounded-r-xl flex flex-col md:flex-row gap-4 md:gap-6 hover:shadow-lg transition-shadow duration-300 item-card-mobile">
            ${item.image_url ? `<img src="${item.image_url}" alt="${item.name}" class="w-24 sm:w-28 md:w-48 max-w-xs mx-auto md:mx-0 my-4 md:my-0 h-auto object-contain rounded-lg shadow-md flex-shrink-0">` : ''}
            <div class="flex-1">
                <h3 class="text-xl md:text-2xl font-bold text-gray-800 mb-4">
                    No.${item.no}: ${item.name}
                </h3>
                <div class="space-y-3 text-gray-700 text-sm md:text-base leading-relaxed">
                    <div><span class="font-semibold">色:</span> <span class="ml-2">${item.color}</span></div>
                    <div class="text-xs md:text-sm text-gray-500">
                        ${item.pair_no ? `対No: ${item.pair_no} (${item.pair_name})` : ''}
                        ${item.hissatsu_name ? `<span class="block md:inline md:ml-3 mt-1 md:mt-0">必殺技: ${item.hissatsu_name}</span>` : ''}
                    </div>
                    <div><span class="font-semibold">動き方:</span> <span class="ml-2">${item.movement}</span></div>
                    <div><span class="font-semibold">説明:</span> <span class="ml-2">${item.description}</span></div>
                    <div class="mt-4 md:mt-6 pt-4 md:pt-6 border-t-2 border-blue-200 space-y-2">
                        <div class="text-green-600 font-medium text-sm md:text-base"><span class="font-bold">ON:</span> <span class="ml-2">${item.on_state}</span></div>
                        <div class="text-red-600 font-medium text-sm md:text-base"><span class="font-bold">OFF:</span> <span class="ml-2">${item.off_state}</span></div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// 動き方の説明を表示
function displayActions(data) {
    const container = document.getElementById('actions-container');
    if (!container || !data.actions) return;

    container.innerHTML = data.actions.map(action => `
        <div class="border-l-4 border-green-500 pl-4 md:pl-6 py-4 bg-gradient-to-r from-green-50 to-transparent rounded-r-lg hover:shadow-md transition-shadow duration-300">
            <h4 class="font-bold text-base md:text-lg text-gray-800 mb-2 md:mb-3">${action.action}</h4>
            <p class="text-gray-700 text-sm md:text-base leading-relaxed">${action.meaning}</p>
        </div>
    `).join('');
}

// ユーティリティ関数
function showLoading() {
    const loading = document.getElementById('loading');
    if (loading) loading.classList.remove('hidden');
}

function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) loading.classList.add('hidden');
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
    }
}

function hideError() {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) errorDiv.classList.add('hidden');
}
