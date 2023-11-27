document.addEventListener('DOMContentLoaded', function() {
  var calendarEl = document.getElementById('calendar');
  var locationId = calendarEl.getAttribute('data-location-id'); 
  var calendar = new FullCalendar.Calendar(calendarEl, {
    // カスタムの設定を追加する場合はここに追加
    headerToolbar: {
      left: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek',
      center: 'title',
      right: 'prev,next today'
    },
    initialView: 'timeGridWeek',
    locale: 'ja',
    buttonText: {
        prev:     '<',
        next:     '>',
        prevYear: '<<',
        nextYear: '>>',
        today:    '今日',
        month:    '月',
        week:     '週',
        day:      '日',
        list:     '一覧'
    },
    slotMinTime: "07:00:00",
    slotMaxTime: "21:00:00",
    allDaySlot: false,
    nowIndicator: true,
    editable: true,
    // イベントデータを非同期で取得
    events: `/api/location_reservations/${locationId}`,
    eventDrop: function(info) {
        var eventId = info.event.id;
        var newStart = info.event.start;
        var newEnd = info.event.end;

        // サーバーに新しい日時情報を送信
        $.ajax({
            url: '/update_reservation_time',
            method: 'POST',
            data: {
                eventId: eventId,
                newStart: newStart,
                newEnd: newEnd
            },
            success: function(response) {
                alert(response.message);
            },
            error: function(error) {
                console.error('Error updating reservation:', error);
            }
        });
    }
  });

  // カレンダーを描画
  calendar.render();
});

document.addEventListener('DOMContentLoaded', function () {
    // 終日予約のチェックボックス
    var isAllDayCheckbox = $('#is_all_day_checkbox');

    // 開始日付と終了日付のフィールド
    var startDateField = $('#start_date_picker');
    var endDateField = $('#end_date_picker');

    // 開始時間と終了時間のフィールド
    var startTimeField = $('#start_time_picker');
    var endTimeField = $('#end_time_picker');

    // 終日予約が変更されたときの処理
    isAllDayCheckbox.change(function () {
        // 終日予約が選択された場合
        if (isAllDayCheckbox.prop('checked')) {
            // 時間のフィールドを無効にする
            startTimeField.prop('disabled', true);
            endTimeField.prop('disabled', true);
        } else {
            // 終日予約が選択されていない場合はフィールドを有効にする
            startTimeField.prop('disabled', false);
            endTimeField.prop('disabled', false);
        }
    });

    // Flatpickrの設定
    flatpickr(startDateField[0], {
        enableTime: false,
        dateFormat: "Y-m-d",
    });

    flatpickr(endDateField[0], {
        enableTime: false,
        dateFormat: "Y-m-d",
    });

    flatpickr(startTimeField[0], {
        enableTime: true,
        noCalendar: true,
        dateFormat: "H:i",
    });

    flatpickr(endTimeField[0], {
        enableTime: true,
        noCalendar: true,
        dateFormat: "H:i",
    });
});
