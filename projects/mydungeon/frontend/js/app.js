// API base URL
const API_BASE = '';  // 同じオリジンの場合は空文字

// ページロード時にセレクトボックスの選択肢を生成
document.addEventListener('DOMContentLoaded', () => {
    initializeDateTimeSelects();
    initializeCompatibilityDateTimeSelects();
    initializeTabs();
});

// タブの初期化
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            switchTab(tabName);
        });
    });
}

// タブ切り替え
function switchTab(tabName) {
    // すべてのタブボタンから active を削除
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });

    // すべてのタブコンテンツから active を削除し、hidden を追加
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
        content.classList.add('hidden');
    });

    // 選択されたタブをアクティブにする
    document.getElementById(`tab-${tabName}`).classList.add('active');
    const targetContainer = document.getElementById(`${tabName}-form-container`);
    targetContainer.classList.remove('hidden');
    targetContainer.classList.add('active');
}

// 年月日時分のセレクトボックスを初期化（個人診断用）
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

// 画像ダウンロード機能（モバイル対応）
function downloadResultImage() {
    const resultImage = document.getElementById('result-image');

    if (!resultImage || !resultImage.src) {
        console.error('画像が見つかりません');
        alert('画像が読み込まれていません。');
        return;
    }

    // ボタンを無効化してフィードバック
    const button = document.getElementById('download-button');
    if (button) {
        button.disabled = true;
        const originalText = button.innerHTML;
        button.innerHTML = '<span class="bg-gradient-to-r from-purple-500 via-blue-500 to-pink-500 bg-clip-text text-transparent font-bold">ダウンロード中...</span>';

        // タイムアウト後に元に戻す
        setTimeout(() => {
            button.disabled = false;
            button.innerHTML = originalText;
        }, 3000);
    }

    // 画像URLを取得
    const imageUrl = resultImage.src;

    // ファイル名を生成（日時ベース）
    const now = new Date();
    const fileName = `mydungeon_result_${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}.png`;

    // モバイル判定
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

    // ダウンロードを実行
    fetch(imageUrl)
        .then(response => {
            if (!response.ok) throw new Error('画像の取得に失敗しました');
            return response.blob();
        })
        .then(blob => {
            // Blobから一時URLを作成
            const url = window.URL.createObjectURL(blob);

            if (isMobile) {
                // モバイルの場合: 新しいタブで開く（より確実）
                const link = document.createElement('a');
                link.href = url;
                link.download = fileName;
                link.target = '_blank';
                link.rel = 'noopener noreferrer';

                // モバイルでのクリックイベントをシミュレート
                document.body.appendChild(link);

                // タッチイベントとクリックイベントの両方をトリガー
                if (typeof link.click === 'function') {
                    link.click();
                } else {
                    // click()が使えない場合の代替手段
                    const evt = new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true
                    });
                    link.dispatchEvent(evt);
                }

                // クリーンアップ（少し遅延させる）
                setTimeout(() => {
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(link);
                }, 100);
            } else {
                // PCの場合: 従来の方法
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = fileName;

                document.body.appendChild(a);
                a.click();

                // クリーンアップ
                setTimeout(() => {
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                }, 100);
            }

            console.log(`画像をダウンロードしました: ${fileName}`);
        })
        .catch(error => {
            console.error('ダウンロードエラー:', error);
            alert('画像のダウンロードに失敗しました。もう一度お試しください。');

            // エラー時もボタンを元に戻す
            if (button) {
                button.disabled = false;
                button.innerHTML = '<span class="bg-gradient-to-r from-purple-500 via-blue-500 to-pink-500 bg-clip-text text-transparent font-bold">画像をダウンロード</span>';
            }
        });
}

// PDF生成・ダウンロード機能
async function downloadResultPDF() {
    try {
        // ライブラリが読み込まれているか確認
        if (typeof window.jspdf === 'undefined' || typeof html2canvas === 'undefined') {
            alert('PDF生成ライブラリの読み込みに失敗しました。ページを再読み込みしてください。');
            return;
        }

        const { jsPDF } = window.jspdf;

        // ローディング表示
        const button = document.getElementById('download-pdf-button');
        const originalText = button.innerHTML;
        button.innerHTML = '<span class="bg-gradient-to-r from-purple-500 via-blue-500 to-pink-500 bg-clip-text text-transparent font-bold">生成中...</span>';
        button.disabled = true;

        // 結果データを取得
        const resultData = JSON.parse(sessionStorage.getItem('result'));
        if (!resultData) {
            alert('結果データが見つかりません');
            button.innerHTML = originalText;
            button.disabled = false;
            return;
        }

        // PDFコンテンツを作成
        const tempDiv = document.createElement('div');
        tempDiv.style.cssText = 'position:absolute;left:-10000px;top:0;width:750px;background:white;padding:30px;font-family:sans-serif;color:#333;';

        // コンテンツHTML生成
        let html = '<div style="font-size:20px;font-weight:bold;text-align:center;margin-bottom:20px;">My Dungeon - 診断結果詳細</div>';

        // 数字
        html += '<div style="font-size:16px;font-weight:bold;margin-top:20px;margin-bottom:8px;border-bottom:2px solid #333;padding-bottom:3px;">あなたの数字</div>';
        const numbers = resultData.numbers || [];
        const hissatsuNumbers = new Set(resultData.hissatsu_numbers || []);
        let numbersText = '';
        numbers.forEach((num, index) => {
            numbersText += hissatsuNumbers.has(num) ? `★${num}` : num;
            if (index < numbers.length - 1) numbersText += ', ';
        });
        html += `<div style="font-size:12px;margin-bottom:20px;">${numbersText}</div>`;

        // 必殺技とアイテム名
        html += '<div style="font-size:16px;font-weight:bold;margin-top:20px;margin-bottom:8px;border-bottom:2px solid #333;padding-bottom:3px;">あなたの必殺技とアイテム</div>';
        if (resultData.hissatsus && resultData.hissatsus.length > 0) {
            resultData.hissatsus.forEach(h => {
                html += `<div style="font-size:11px;font-weight:bold;margin:2px 0;">【必殺技】${h.name}</div>`;
            });
        }
        if (resultData.items && resultData.items.length > 0) {
            resultData.items.forEach(item => {
                html += `<div style="font-size:11px;margin:2px 0;">No.${item.no}  ${item.name}</div>`;
            });
        }
        html += '<div style="margin-bottom:20px;"></div>';

        // 色ごとの枚数
        html += '<div style="font-size:16px;font-weight:bold;margin-top:20px;margin-bottom:8px;border-bottom:2px solid #333;padding-bottom:3px;">色ごとの枚数</div>';
        if (resultData.color_counts && resultData.color_counts.color_systems) {
            resultData.color_counts.color_systems.forEach(system => {
                html += `<div style="font-size:11px;font-weight:bold;margin:8px 0 3px;">${system.name}: ${system.meaning} - ${system.total_count}枚</div>`;
                system.colors.forEach(color => {
                    html += `<div style="font-size:10px;margin-left:15px;">${color.name}: ${color.meaning} - ${color.count}枚</div>`;
                });
            });
        }
        html += '<div style="margin-bottom:20px;"></div>';

        // 必殺技詳細
        if (resultData.hissatsus && resultData.hissatsus.length > 0) {
            html += '<div style="font-size:16px;font-weight:bold;margin-top:20px;margin-bottom:8px;border-bottom:2px solid #333;padding-bottom:3px;">持っている必殺技</div>';
            resultData.hissatsus.forEach(h => {
                html += `<div style="margin:15px 0;padding:10px;background:#fafafa;border-radius:8px;font-size:10px;">
                    <div style="font-weight:bold;font-size:12px;margin-bottom:5px;">${h.name}</div>
                    <div>色: ${h.color}</div><div>意味: ${h.meaning}</div><div>動き方: ${h.movement}</div>
                    <div>基本姿勢: ${h.basic_posture}</div><div>才能: ${h.talent}</div>
                    <div>特性: ${h.characteristics}</div><div>アドバイス: ${h.advice}</div>
                    <div style="color:#16a34a;"><span style="font-weight:bold;">ON:</span> ${h.on_state}</div>
                    <div style="color:#dc2626;"><span style="font-weight:bold;">OFF:</span> ${h.off_state}</div>
                </div>`;
            });
        }

        // アイテム詳細
        html += '<div style="font-size:16px;font-weight:bold;margin-top:20px;margin-bottom:8px;border-bottom:2px solid #333;padding-bottom:3px;">持っているアイテム</div>';
        if (resultData.items && resultData.items.length > 0) {
            resultData.items.forEach(item => {
                html += `<div style="margin:15px 0;padding:10px;background:#fafafa;border-radius:8px;font-size:10px;">
                    <div style="font-weight:bold;font-size:12px;margin-bottom:5px;">No.${item.no}: ${item.name}</div>
                    <div>色: ${item.color}</div><div>動き方: ${item.movement}</div>
                    <div>説明: ${item.description}</div>
                    <div style="color:#16a34a;"><span style="font-weight:bold;">ON:</span> ${item.on_state}</div>
                    <div style="color:#dc2626;"><span style="font-weight:bold;">OFF:</span> ${item.off_state}</div>
                </div>`;
            });
        }

        // 動き方
        if (resultData.actions && resultData.actions.length > 0) {
            html += '<div style="font-size:16px;font-weight:bold;margin-top:20px;margin-bottom:8px;border-bottom:2px solid #333;padding-bottom:3px;">動き方の説明</div>';
            resultData.actions.forEach(action => {
                html += `<div style="margin:10px 0;font-size:10px;">
                    <div style="font-weight:bold;">${action.action}</div>
                    <div style="margin-left:10px;">${action.meaning}</div>
                </div>`;
            });
        }

        tempDiv.innerHTML = html;
        document.body.appendChild(tempDiv);

        // キャンバスに変換
        const canvas = await html2canvas(tempDiv, {
            scale: 2,
            useCORS: true,
            backgroundColor: '#ffffff'
        });

        document.body.removeChild(tempDiv);

        // PDF作成
        const imgData = canvas.toDataURL('image/jpeg', 0.95);
        const pdf = new jsPDF('p', 'mm', 'a4');
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = pdf.internal.pageSize.getHeight();

        const margin = 15;
        const imgWidth = pdfWidth - (margin * 2);
        const imgHeight = (canvas.height * imgWidth) / canvas.width;
        const pageContentHeight = pdfHeight - (margin * 2);

        // ページ数を計算
        const totalPages = Math.ceil(imgHeight / pageContentHeight);

        for (let pageNum = 0; pageNum < totalPages; pageNum++) {
            if (pageNum > 0) {
                pdf.addPage();
            }

            const yStart = pageNum * pageContentHeight;
            const yEnd = Math.min((pageNum + 1) * pageContentHeight, imgHeight);
            const actualHeight = yEnd - yStart;

            // キャンバスから該当部分を切り出し
            const pageCanvas = document.createElement('canvas');
            const canvasYStart = (yStart / imgWidth) * canvas.width;
            const canvasHeight = (actualHeight / imgWidth) * canvas.width;

            pageCanvas.width = canvas.width;
            pageCanvas.height = canvasHeight;

            const ctx = pageCanvas.getContext('2d');
            ctx.drawImage(
                canvas,
                0, canvasYStart,
                canvas.width, canvasHeight,
                0, 0,
                canvas.width, canvasHeight
            );

            const pageImgData = pageCanvas.toDataURL('image/jpeg', 0.95);
            pdf.addImage(pageImgData, 'JPEG', margin, margin, imgWidth, actualHeight);
        }

        // ファイル名生成
        const now = new Date();
        const fileName = `mydungeon_details_${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}.pdf`;

        pdf.save(fileName);

        console.log(`PDFをダウンロードしました: ${fileName}`);

        button.innerHTML = originalText;
        button.disabled = false;

    } catch (error) {
        console.error('PDF生成エラー:', error);
        alert('PDFの生成に失敗しました。もう一度お試しください。');

        const button = document.getElementById('download-pdf-button');
        if (button) {
            button.innerHTML = '<span class="bg-gradient-to-r from-purple-500 via-blue-500 to-pink-500 bg-clip-text text-transparent font-bold">詳細をPDFで保存</span>';
            button.disabled = false;
        }
    }
}

// ========================================
// 相性診断機能
// ========================================

// 相性診断フォームの日時セレクトを初期化
function initializeCompatibilityDateTimeSelects() {
    const person1Selects = {
        year: document.getElementById('person1-birth-year'),
        month: document.getElementById('person1-birth-month'),
        day: document.getElementById('person1-birth-day'),
        hour: document.getElementById('person1-birth-hour'),
        minute: document.getElementById('person1-birth-minute')
    };

    const person2Selects = {
        year: document.getElementById('person2-birth-year'),
        month: document.getElementById('person2-birth-month'),
        day: document.getElementById('person2-birth-day'),
        hour: document.getElementById('person2-birth-hour'),
        minute: document.getElementById('person2-birth-minute')
    };

    if (!person1Selects.year) return; // 入力画面でない場合は処理しない

    // Person1とPerson2の両方のセレクトを初期化
    [person1Selects, person2Selects].forEach(selects => {
        // 年の選択肢を生成（1900年〜現在年）
        const currentYear = new Date().getFullYear();
        for (let year = currentYear; year >= 1900; year--) {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year + '年';
            selects.year.appendChild(option);
        }

        // 月の選択肢を生成（1〜12月）
        for (let month = 1; month <= 12; month++) {
            const option = document.createElement('option');
            option.value = month;
            option.textContent = month + '月';
            selects.month.appendChild(option);
        }

        // 日の選択肢を生成（1〜31日）
        for (let day = 1; day <= 31; day++) {
            const option = document.createElement('option');
            option.value = day;
            option.textContent = day + '日';
            selects.day.appendChild(option);
        }

        // 時の選択肢を生成（0〜23時）
        for (let hour = 0; hour <= 23; hour++) {
            const option = document.createElement('option');
            option.value = hour;
            option.textContent = hour + '時';
            selects.hour.appendChild(option);
        }

        // 分の選択肢を生成（0〜59分）
        for (let minute = 0; minute <= 59; minute++) {
            const option = document.createElement('option');
            option.value = minute;
            option.textContent = minute + '分';
            selects.minute.appendChild(option);
        }
    });
}

// 相性診断フォームの処理
document.getElementById('compatibility-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Person1のデータ取得
    const person1Name = document.getElementById('person1-name').value.trim();
    const person1Year = document.getElementById('person1-birth-year').value;
    const person1Month = document.getElementById('person1-birth-month').value;
    const person1Day = document.getElementById('person1-birth-day').value;
    const person1Hour = document.getElementById('person1-birth-hour').value;
    const person1Minute = document.getElementById('person1-birth-minute').value;

    // Person2のデータ取得
    const person2Name = document.getElementById('person2-name').value.trim();
    const person2Year = document.getElementById('person2-birth-year').value;
    const person2Month = document.getElementById('person2-birth-month').value;
    const person2Day = document.getElementById('person2-birth-day').value;
    const person2Hour = document.getElementById('person2-birth-hour').value;
    const person2Minute = document.getElementById('person2-birth-minute').value;

    // 生年月日と時刻をフォーマット
    const person1Birthdate = `${person1Year}-${String(person1Month).padStart(2, '0')}-${String(person1Day).padStart(2, '0')}`;
    const person1Birthtime = `${String(person1Hour).padStart(2, '0')}:${String(person1Minute).padStart(2, '0')}`;
    const person2Birthdate = `${person2Year}-${String(person2Month).padStart(2, '0')}-${String(person2Day).padStart(2, '0')}`;
    const person2Birthtime = `${String(person2Hour).padStart(2, '0')}:${String(person2Minute).padStart(2, '0')}`;

    // ローディング表示
    showCompatibilityLoading();
    hideCompatibilityError();

    try {
        const response = await fetch(`${API_BASE}/api/generate-compatibility`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                person1_name: person1Name || null,
                person1_birthdate: person1Birthdate,
                person1_birthtime: person1Birthtime,
                person2_name: person2Name || null,
                person2_birthdate: person2Birthdate,
                person2_birthtime: person2Birthtime
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '相性診断に失敗しました');
        }

        const resultData = await response.json();

        // セッションストレージに保存
        sessionStorage.setItem('compatibility-result', JSON.stringify(resultData));

        // 結果ページに遷移
        window.location.href = '/static/result_compatibility.html';

    } catch (error) {
        console.error('Error:', error);
        showCompatibilityError(error.message);
    } finally {
        hideCompatibilityLoading();
    }
});

// 相性診断用のローディング表示
function showCompatibilityLoading() {
    const loading = document.getElementById('compatibility-loading');
    const form = document.getElementById('compatibility-form');
    if (loading && form) {
        loading.classList.remove('hidden');
        form.style.display = 'none';
    }
}

function hideCompatibilityLoading() {
    const loading = document.getElementById('compatibility-loading');
    const form = document.getElementById('compatibility-form');
    if (loading && form) {
        loading.classList.add('hidden');
        form.style.display = 'block';
    }
}

// 相性診断用のエラー表示
function showCompatibilityError(message) {
    const errorDiv = document.getElementById('compatibility-error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
    }
}

function hideCompatibilityError() {
    const errorDiv = document.getElementById('compatibility-error-message');
    if (errorDiv) {
        errorDiv.classList.add('hidden');
    }
}
