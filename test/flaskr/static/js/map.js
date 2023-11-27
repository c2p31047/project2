let map;
let marker;

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 0, lng: 0 },
        zoom: 13
    });

    marker = new google.maps.Marker({
        map: map,
        position: { lat: 0, lng: 0 },
        title: '現在の位置'
    });

    // 位置情報取得ボタンのクリックイベント
    document.getElementById('getLocation').addEventListener('click', getLocation);

    // 数秒ごとに位置情報を更新
    setInterval(getLocation, 5000); // 5000 milliseconds = 5 seconds
}

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
            const location = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };

            // マーカーの位置を更新
            marker.setPosition(location);

            // 地図を指定位置に移動
            map.setCenter(location);

            // 位置情報を表示
            document.getElementById('locationText').textContent = '緯度: ' + location.lat + ', 経度: ' + location.lng;
        }, function () {
            alert('位置情報を取得できませんでした。');
        });
    } else {
        alert('ブラウザが位置情報をサポートしていません。');
    }
}

// Google Maps APIの非同期読み込み
function loadScript() {
    const script = document.createElement('script');
    script.src = 'https://maps.googleapis.com/maps/api/js?key=AIzaSyAFcyIINxfRta3BSgR66oUdlS6BPEcnLsA&callback=initMap'; // Replace YOUR_API_KEY with your actual API key
    script.defer = true;
    document.head.appendChild(script);
}

// ページ読み込み後にGoogle Maps APIを読み込む
window.addEventListener('load', loadScript);
// ページ読み込み後にGoogle Maps APIを読み込む
window.addEventListener('load', loadScript);
