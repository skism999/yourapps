// 相性診断結果表示用JavaScript

// ページロード時に結果を表示
window.addEventListener('DOMContentLoaded', () => {
    displayCompatibilityResult();

    // ダウンロードボタンのイベントリスナー
    document.getElementById('download-button')?.addEventListener('click', downloadCompatibilityImage);
    // PDFダウンロードボタンのイベントリスナー
    document.getElementById('download-pdf-button')?.addEventListener('click', downloadCompatibilityPDF);
});

// 相性診断結果を表示
function displayCompatibilityResult() {
    const resultData = JSON.parse(sessionStorage.getItem('compatibility-result'));

    if (!resultData) {
        window.location.href = '/';
        return;
    }

    // 各セクションを表示
    displayCompatibilityImage(resultData);
    displayColorCodedNumbers('person1', resultData.person1);
    displayColorCodedNumbers('person2', resultData.person2);
    displayJointHissatsus(resultData.joint_hissatsus);
    displaySynergyHissatsus('person1', resultData.person1_synergy_hissatsus, resultData.person1.name, resultData.person2.name);
    displaySynergyHissatsus('person2', resultData.person2_synergy_hissatsus, resultData.person2.name, resultData.person1.name);
    displayBothHaveHissatsus(resultData.both_have_hissatsus);
    displayOtherItems(resultData);
    displayColorCounts(resultData);
    displayActions(resultData.actions);
}

// 相性画像を表示
function displayCompatibilityImage(data) {
    const imgElement = document.getElementById('compatibility-image');
    if (imgElement && data.image_url) {
        imgElement.src = data.image_url;
        imgElement.onerror = () => {
            console.error('画像の読み込みに失敗しました');
        };
    }
}

// 色分けされた数字を表示
function displayColorCodedNumbers(person, personData) {
    const container = document.getElementById(`${person}-numbers-container`);
    if (!container) return;

    const purpleNumbers = new Set(personData.joint_numbers || []);
    const redNumbers = new Set(personData.both_have_numbers || []);
    const blueNumbers = new Set(personData.person1_synergy_numbers || []);
    const greenNumbers = new Set(personData.person2_synergy_numbers || []);
    const soloNumbers = new Set(personData.solo_hissatsu_numbers || []);

    container.innerHTML = personData.numbers.map(num => {
        let colorClass;
        if (purpleNumbers.has(num)) {
            colorClass = 'bg-gradient-to-br from-purple-500 to-purple-600 text-white shadow-lg';
        } else if (blueNumbers.has(num)) {
            colorClass = 'bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg';
        } else if (greenNumbers.has(num)) {
            colorClass = 'bg-gradient-to-br from-green-500 to-green-600 text-white shadow-lg';
        } else if (redNumbers.has(num)) {
            colorClass = 'bg-gradient-to-br from-red-500 to-red-600 text-white shadow-lg';
        } else if (soloNumbers.has(num)) {
            colorClass = 'bg-gradient-to-br from-gray-600 to-gray-700 text-white shadow-lg';
        } else {
            // その他のアイテム（必殺技に含まれない数字）は薄いグレー
            colorClass = 'bg-gradient-to-br from-gray-200 to-gray-300 text-gray-700 shadow-sm';
        }

        return `<span class="${colorClass} px-6 py-3 rounded-xl font-bold text-lg hover:scale-110 hover:shadow-xl transition-all duration-200">${num}</span>`;
    }).join('');
}

// 二人で発動する必殺技を表示
function displayJointHissatsus(hissatsus) {
    const container = document.getElementById('joint-hissatsus-container');
    if (!container) return;

    if (!hissatsus || hissatsus.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-center py-4">該当する必殺技はありません</p>';
        return;
    }

    container.innerHTML = hissatsus.map(h => `
        <div class="pl-4 md:pl-8 py-6 bg-gradient-to-r from-purple-50 to-transparent rounded-r-xl hover:shadow-lg transition-shadow duration-300 mb-8">
            ${h.image_url ? `<div class="mb-6"><img src="${h.image_url}" alt="${h.name}" class="w-full max-w-md md:max-w-lg h-auto object-contain rounded-lg shadow-md mx-auto"></div>` : ''}
            <div>
                <h3 class="text-xl md:text-2xl font-bold text-purple-800 mb-4 md:mb-6">
                    ${h.name}
                </h3>
                <div class="space-y-3 text-gray-700 text-sm md:text-base leading-relaxed">
                    <div><span class="font-semibold">色:</span> <span class="ml-2">${h.color}</span></div>
                    <div><span class="font-semibold">意味:</span> <span class="ml-2">${h.meaning}</span></div>
                    <div><span class="font-semibold">動き方:</span> <span class="ml-2">${h.movement}</span></div>
                    <div><span class="font-semibold">基本姿勢:</span> <span class="ml-2">${h.basic_posture}</span></div>
                    <div><span class="font-semibold">才能:</span> <span class="ml-2">${h.talent}</span></div>
                    <div><span class="font-semibold">特性:</span> <span class="ml-2">${h.characteristics}</span></div>
                    <div class="pt-2"><span class="font-semibold text-purple-600">アドバイス:</span> <span class="ml-2">${h.advice}</span></div>
                    <div class="mt-4 md:mt-6 pt-4 md:pt-6 border-t-2 border-purple-200 space-y-2">
                        <div class="text-green-600 font-medium text-sm md:text-base"><span class="font-bold">ON:</span> <span class="ml-2">${h.on_state}</span></div>
                        <div class="text-red-600 font-medium text-sm md:text-base"><span class="font-bold">OFF:</span> <span class="ml-2">${h.off_state}</span></div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// お互い持っている必殺技を表示
function displayBothHaveHissatsus(hissatsus) {
    const container = document.getElementById('both-have-hissatsus-container');
    if (!container) return;

    if (!hissatsus || hissatsus.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-center py-4">該当する必殺技はありません</p>';
        return;
    }

    container.innerHTML = hissatsus.map(h => `
        <div class="pl-4 md:pl-8 py-6 bg-gradient-to-r from-red-50 to-transparent rounded-r-xl hover:shadow-lg transition-shadow duration-300 mb-8">
            ${h.image_url ? `<div class="mb-6"><img src="${h.image_url}" alt="${h.name}" class="w-full max-w-md md:max-w-lg h-auto object-contain rounded-lg shadow-md mx-auto"></div>` : ''}
            <div>
                <h3 class="text-xl md:text-2xl font-bold text-red-800 mb-4 md:mb-6">
                    ${h.name}
                </h3>
                <div class="space-y-3 text-gray-700 text-sm md:text-base leading-relaxed">
                    <div><span class="font-semibold">色:</span> <span class="ml-2">${h.color}</span></div>
                    <div><span class="font-semibold">意味:</span> <span class="ml-2">${h.meaning}</span></div>
                    <div><span class="font-semibold">動き方:</span> <span class="ml-2">${h.movement}</span></div>
                    <div><span class="font-semibold">基本姿勢:</span> <span class="ml-2">${h.basic_posture}</span></div>
                    <div><span class="font-semibold">才能:</span> <span class="ml-2">${h.talent}</span></div>
                    <div><span class="font-semibold">特性:</span> <span class="ml-2">${h.characteristics}</span></div>
                    <div class="pt-2"><span class="font-semibold text-red-600">アドバイス:</span> <span class="ml-2">${h.advice}</span></div>
                    <div class="mt-4 md:mt-6 pt-4 md:pt-6 border-t-2 border-red-200 space-y-2">
                        <div class="text-green-600 font-medium text-sm md:text-base"><span class="font-bold">ON:</span> <span class="ml-2">${h.on_state}</span></div>
                        <div class="text-red-600 font-medium text-sm md:text-base"><span class="font-bold">OFF:</span> <span class="ml-2">${h.off_state}</span></div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// 相乗効果の必殺技を表示
function displaySynergyHissatsus(person, hissatsus, activator, supporter) {
    const container = document.getElementById(`${person}-synergy-container`);
    if (!container) return;

    if (!hissatsus || hissatsus.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-center py-4">該当する必殺技はありません</p>';
        return;
    }

    const bgColor = person === 'person1' ? 'from-blue-50' : 'from-green-50';
    const textColor = person === 'person1' ? 'text-blue-800' : 'text-green-800';
    const borderColor = person === 'person1' ? 'border-blue-200' : 'border-green-200';

    container.innerHTML = hissatsus.map(h => `
        <div class="pl-4 md:pl-8 py-6 bg-gradient-to-r ${bgColor} to-transparent rounded-r-xl hover:shadow-lg transition-shadow duration-300 mb-8">
            ${h.image_url ? `<div class="mb-6"><img src="${h.image_url}" alt="${h.name}" class="w-full max-w-md md:max-w-lg h-auto object-contain rounded-lg shadow-md mx-auto"></div>` : ''}
            <div>
                <h3 class="text-xl md:text-2xl font-bold ${textColor} mb-4 md:mb-6">
                    ${h.name}
                </h3>
                <div class="space-y-3 text-gray-700 text-sm md:text-base leading-relaxed">
                    <div><span class="font-semibold">色:</span> <span class="ml-2">${h.color}</span></div>
                    <div><span class="font-semibold">意味:</span> <span class="ml-2">${h.meaning}</span></div>
                    <div><span class="font-semibold">動き方:</span> <span class="ml-2">${h.movement}</span></div>
                    <div><span class="font-semibold">基本姿勢:</span> <span class="ml-2">${h.basic_posture}</span></div>
                    <div><span class="font-semibold">才能:</span> <span class="ml-2">${h.talent}</span></div>
                    <div><span class="font-semibold">特性:</span> <span class="ml-2">${h.characteristics}</span></div>
                    <div class="pt-2"><span class="font-semibold ${textColor}">アドバイス:</span> <span class="ml-2">${h.advice}</span></div>
                    <div class="mt-4 md:mt-6 pt-4 md:pt-6 border-t-2 ${borderColor} space-y-2">
                        <div class="text-green-600 font-medium text-sm md:text-base"><span class="font-bold">ON:</span> <span class="ml-2">${h.on_state}</span></div>
                        <div class="text-red-600 font-medium text-sm md:text-base"><span class="font-bold">OFF:</span> <span class="ml-2">${h.off_state}</span></div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// その他の必殺技とアイテムを表示
function displayOtherItems(data) {
    const container = document.getElementById('other-items-container');
    if (!container) return;

    let html = '';

    // Person1の単独必殺技
    if (data.person1.solo_hissatsus && data.person1.solo_hissatsus.length > 0) {
        html += `<h4 class="font-bold text-xl text-gray-800 mb-4">${data.person1.name || 'あなた'}の必殺技</h4>`;
        html += data.person1.solo_hissatsus.map(h => `
            <div class="pl-4 md:pl-8 py-6 bg-gradient-to-r from-gray-50 to-transparent rounded-r-xl hover:shadow-lg transition-shadow duration-300 mb-8">
                ${h.image_url ? `<div class="mb-6"><img src="${h.image_url}" alt="${h.name}" class="w-full max-w-md md:max-w-lg h-auto object-contain rounded-lg shadow-md mx-auto"></div>` : ''}
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
                        <div class="pt-2"><span class="font-semibold text-gray-600">アドバイス:</span> <span class="ml-2">${h.advice}</span></div>
                        <div class="mt-4 md:mt-6 pt-4 md:pt-6 border-t-2 border-gray-200 space-y-2">
                            <div class="text-green-600 font-medium text-sm md:text-base"><span class="font-bold">ON:</span> <span class="ml-2">${h.on_state}</span></div>
                            <div class="text-red-600 font-medium text-sm md:text-base"><span class="font-bold">OFF:</span> <span class="ml-2">${h.off_state}</span></div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Person2の単独必殺技
    if (data.person2.solo_hissatsus && data.person2.solo_hissatsus.length > 0) {
        html += `<h4 class="font-bold text-xl text-gray-800 mb-4 mt-8">${data.person2.name || '相手'}の必殺技</h4>`;
        html += data.person2.solo_hissatsus.map(h => `
            <div class="pl-4 md:pl-8 py-6 bg-gradient-to-r from-gray-50 to-transparent rounded-r-xl hover:shadow-lg transition-shadow duration-300 mb-8">
                ${h.image_url ? `<div class="mb-6"><img src="${h.image_url}" alt="${h.name}" class="w-full max-w-md md:max-w-lg h-auto object-contain rounded-lg shadow-md mx-auto"></div>` : ''}
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
                        <div class="pt-2"><span class="font-semibold text-gray-600">アドバイス:</span> <span class="ml-2">${h.advice}</span></div>
                        <div class="mt-4 md:mt-6 pt-4 md:pt-6 border-t-2 border-gray-200 space-y-2">
                            <div class="text-green-600 font-medium text-sm md:text-base"><span class="font-bold">ON:</span> <span class="ml-2">${h.on_state}</span></div>
                            <div class="text-red-600 font-medium text-sm md:text-base"><span class="font-bold">OFF:</span> <span class="ml-2">${h.off_state}</span></div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Person1のアイテム
    if (data.person1.items && data.person1.items.length > 0) {
        html += `<h4 class="font-bold text-xl text-gray-800 mb-4 mt-8">${data.person1.name || 'あなた'}のアイテム</h4>`;
        html += data.person1.items.map(item => `
            <div class="pl-4 md:pl-8 py-6 bg-gradient-to-r from-blue-50 to-transparent rounded-r-xl flex flex-col md:flex-row gap-4 md:gap-6 hover:shadow-lg transition-shadow duration-300 mb-6">
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

    // Person2のアイテム
    if (data.person2.items && data.person2.items.length > 0) {
        html += `<h4 class="font-bold text-xl text-gray-800 mb-4 mt-8">${data.person2.name || '相手'}のアイテム</h4>`;
        html += data.person2.items.map(item => `
            <div class="pl-4 md:pl-8 py-6 bg-gradient-to-r from-purple-50 to-transparent rounded-r-xl flex flex-col md:flex-row gap-4 md:gap-6 hover:shadow-lg transition-shadow duration-300 mb-6">
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
                        <div class="mt-4 md:mt-6 pt-4 md:pt-6 border-t-2 border-purple-200 space-y-2">
                            <div class="text-green-600 font-medium text-sm md:text-base"><span class="font-bold">ON:</span> <span class="ml-2">${item.on_state}</span></div>
                            <div class="text-red-600 font-medium text-sm md:text-base"><span class="font-bold">OFF:</span> <span class="ml-2">${item.off_state}</span></div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    container.innerHTML = html || '<p class="text-gray-500 text-center py-4">その他の項目はありません</p>';
}

// 色ごとの枚数を表示（相性診断の必殺技のみ）
function displayColorCounts(data) {
    const container = document.getElementById('color-counts-container');
    if (!container || !data) return;

    // 相性診断の4カテゴリの必殺技を集める
    const allHissatsus = [
        ...(data.joint_hissatsus || []),
        ...(data.both_have_hissatsus || []),
        ...(data.person1_synergy_hissatsus || []),
        ...(data.person2_synergy_hissatsus || [])
    ];

    if (allHissatsus.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-center py-4">必殺技がありません</p>';
        return;
    }

    // 色ごとの枚数を計算
    const colorCounts = {};
    allHissatsus.forEach(h => {
        const color = h.color;
        if (color) {
            colorCounts[color] = (colorCounts[color] || 0) + 1;
        }
    });

    // 色の順序と意味を定義
    const colorInfo = {
        '赤': { order: 1, meaning: '俺らしくいることが世界を救う' },
        '桃': { order: 2, meaning: '俺大好きパワーが世界を救う' },
        '緑': { order: 3, meaning: '仲間と俺とで世界を救う' },
        '黄緑': { order: 4, meaning: '仲間を守る本能が世界を救う' },
        '青': { order: 5, meaning: '社会にシェアすることで世界を救う' },
        '水': { order: 6, meaning: '社会で遊ぶことが世界を救う' },
        '黄': { order: 7, meaning: '世界最強の俺が世界を救う' }
    };

    // 色ごとの枚数を表示
    const sortedColors = Object.keys(colorCounts).sort((a, b) => {
        return (colorInfo[a]?.order || 999) - (colorInfo[b]?.order || 999);
    });

    container.innerHTML = sortedColors.map(color => `
        <div class="p-6 bg-gradient-to-r from-purple-50 via-blue-50 to-pink-50 rounded-xl shadow-md">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-xl font-bold text-gray-800">${color}</h3>
                <span class="text-3xl font-bold text-purple-600">${colorCounts[color]}枚</span>
            </div>
            <p class="text-gray-600 text-sm">${colorInfo[color]?.meaning || ''}</p>
        </div>
    `).join('');
}

// 動き方の説明を表示
function displayActions(actions) {
    const container = document.getElementById('actions-container');
    if (!container || !actions) return;

    container.innerHTML = actions.map(action => `
        <div class="border-l-4 border-green-500 pl-6 py-4 bg-green-50 rounded-r-xl">
            <h3 class="font-bold text-lg text-gray-800">${action.action}</h3>
            <p class="text-gray-600 mt-2">${action.meaning}</p>
        </div>
    `).join('');
}

// 画像ダウンロード（既存のapp.jsのロジックを再利用）
async function downloadCompatibilityImage() {
    const button = document.getElementById('download-button');
    const originalText = button.innerHTML;

    try {
        button.innerHTML = 'ダウンロード中...';
        button.disabled = true;

        const imgElement = document.getElementById('compatibility-image');
        const imgSrc = imgElement.src;

        const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

        const response = await fetch(imgSrc);
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.href = blobUrl;

        const timestamp = new Date().toISOString().replace(/[-:]/g, '').split('.')[0];
        const fileName = `mydungeon_compatibility_${timestamp}.png`;
        link.download = fileName;

        if (isMobile) {
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
        }

        link.click();

        setTimeout(() => {
            URL.revokeObjectURL(blobUrl);
            link.remove();
        }, 100);

        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
        }, 3000);

    } catch (error) {
        console.error('ダウンロードエラー:', error);
        alert('画像のダウンロードに失敗しました');
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// PDF生成・ダウンロード機能
async function downloadCompatibilityPDF() {
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
        const resultData = JSON.parse(sessionStorage.getItem('compatibility-result'));
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
        let html = '<div style="font-size:20px;font-weight:bold;text-align:center;margin-bottom:20px;">My Dungeon - 相性診断結果詳細</div>';

        // 診断情報
        html += `<div style="font-size:12px;margin-bottom:15px;">`;
        html += `<div>あなた: ${resultData.person1.name || '名前なし'} (${resultData.person1.birthdate} ${resultData.person1.birthtime})</div>`;
        html += `<div>相手: ${resultData.person2.name || '名前なし'} (${resultData.person2.birthdate} ${resultData.person2.birthtime})</div>`;
        html += `</div>`;

        // 2人の数字
        html += '<div style="font-size:16px;font-weight:bold;margin-top:20px;margin-bottom:8px;border-bottom:2px solid #333;padding-bottom:3px;">2人の数字</div>';
        html += `<div style="font-size:11px;margin-bottom:5px;"><strong>あなた:</strong> ${resultData.person1.numbers.join(', ')}</div>`;
        html += `<div style="font-size:11px;margin-bottom:15px;"><strong>相手:</strong> ${resultData.person2.numbers.join(', ')}</div>`;

        // 二人で発動する必殺技
        if (resultData.joint_hissatsus && resultData.joint_hissatsus.length > 0) {
            html += '<div style="font-size:16px;font-weight:bold;margin-top:20px;margin-bottom:8px;border-bottom:2px solid #333;padding-bottom:3px;">二人で発動する必殺技</div>';
            resultData.joint_hissatsus.forEach(h => {
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

        // お互い持っている必殺技
        if (resultData.both_have_hissatsus && resultData.both_have_hissatsus.length > 0) {
            html += '<div style="font-size:16px;font-weight:bold;margin-top:20px;margin-bottom:8px;border-bottom:2px solid #333;padding-bottom:3px;">お互い持っている必殺技（相乗効果×2）</div>';
            resultData.both_have_hissatsus.forEach(h => {
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

        // あなたの相乗効果
        if (resultData.person1_synergy_hissatsus && resultData.person1_synergy_hissatsus.length > 0) {
            html += '<div style="font-size:16px;font-weight:bold;margin-top:20px;margin-bottom:8px;border-bottom:2px solid #333;padding-bottom:3px;">あなただけで発動するが相手がいて相乗効果がある必殺技</div>';
            resultData.person1_synergy_hissatsus.forEach(h => {
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

        // 相手の相乗効果
        if (resultData.person2_synergy_hissatsus && resultData.person2_synergy_hissatsus.length > 0) {
            html += '<div style="font-size:16px;font-weight:bold;margin-top:20px;margin-bottom:8px;border-bottom:2px solid #333;padding-bottom:3px;">相手だけで発動するがあなたがいて相乗効果がある必殺技</div>';
            resultData.person2_synergy_hissatsus.forEach(h => {
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

        // あなたの単独必殺技
        if (resultData.person1.solo_hissatsus && resultData.person1.solo_hissatsus.length > 0) {
            html += '<div style="font-size:16px;font-weight:bold;margin-top:20px;margin-bottom:8px;border-bottom:2px solid #333;padding-bottom:3px;">あなたの必殺技</div>';
            resultData.person1.solo_hissatsus.forEach(h => {
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

        // 相手の単独必殺技
        if (resultData.person2.solo_hissatsus && resultData.person2.solo_hissatsus.length > 0) {
            html += '<div style="font-size:16px;font-weight:bold;margin-top:20px;margin-bottom:8px;border-bottom:2px solid #333;padding-bottom:3px;">相手の必殺技</div>';
            resultData.person2.solo_hissatsus.forEach(h => {
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

        // あなたのアイテム
        if (resultData.person1.items && resultData.person1.items.length > 0) {
            html += '<div style="font-size:16px;font-weight:bold;margin-top:20px;margin-bottom:8px;border-bottom:2px solid #333;padding-bottom:3px;">あなたのアイテム</div>';
            resultData.person1.items.forEach(item => {
                html += `<div style="margin:15px 0;padding:10px;background:#fafafa;border-radius:8px;font-size:10px;">
                    <div style="font-weight:bold;font-size:12px;margin-bottom:5px;">No.${item.no}: ${item.name}</div>
                    <div>色: ${item.color}</div><div>動き方: ${item.movement}</div>
                    <div>説明: ${item.description}</div>
                    <div style="color:#16a34a;"><span style="font-weight:bold;">ON:</span> ${item.on_state}</div>
                    <div style="color:#dc2626;"><span style="font-weight:bold;">OFF:</span> ${item.off_state}</div>
                </div>`;
            });
        }

        // 相手のアイテム
        if (resultData.person2.items && resultData.person2.items.length > 0) {
            html += '<div style="font-size:16px;font-weight:bold;margin-top:20px;margin-bottom:8px;border-bottom:2px solid #333;padding-bottom:3px;">相手のアイテム</div>';
            resultData.person2.items.forEach(item => {
                html += `<div style="margin:15px 0;padding:10px;background:#fafafa;border-radius:8px;font-size:10px;">
                    <div style="font-weight:bold;font-size:12px;margin-bottom:5px;">No.${item.no}: ${item.name}</div>
                    <div>色: ${item.color}</div><div>動き方: ${item.movement}</div>
                    <div>説明: ${item.description}</div>
                    <div style="color:#16a34a;"><span style="font-weight:bold;">ON:</span> ${item.on_state}</div>
                    <div style="color:#dc2626;"><span style="font-weight:bold;">OFF:</span> ${item.off_state}</div>
                </div>`;
            });
        }

        // 動き方の説明
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

        // HTMLをキャンバスに変換
        const canvas = await html2canvas(tempDiv, {
            scale: 2,
            useCORS: true,
            logging: false,
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

        // ページ分割が必要な場合
        if (imgHeight > pdfHeight - (margin * 2)) {
            const pageCount = Math.ceil(imgHeight / (pdfHeight - (margin * 2)));
            const pageHeight = pdfHeight - (margin * 2);

            for (let i = 0; i < pageCount; i++) {
                if (i > 0) pdf.addPage();

                const sourceY = i * pageHeight * (canvas.width / imgWidth);
                const sourceHeight = Math.min(pageHeight * (canvas.width / imgWidth), canvas.height - sourceY);
                const actualHeight = (sourceHeight * imgWidth) / canvas.width;

                const pageCanvas = document.createElement('canvas');
                pageCanvas.width = canvas.width;
                pageCanvas.height = sourceHeight;
                const pageCtx = pageCanvas.getContext('2d');
                pageCtx.drawImage(
                    canvas,
                    0, sourceY,
                    canvas.width, sourceHeight,
                    0, 0,
                    canvas.width, sourceHeight
                );

                const pageImgData = pageCanvas.toDataURL('image/jpeg', 0.95);
                pdf.addImage(pageImgData, 'JPEG', margin, margin, imgWidth, actualHeight);
            }
        } else {
            pdf.addImage(imgData, 'JPEG', margin, margin, imgWidth, imgHeight);
        }

        // ファイル名生成
        const now = new Date();
        const fileName = `mydungeon_compatibility_${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}.pdf`;

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
