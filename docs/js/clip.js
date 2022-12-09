function copyUrl() {
  //開いているページのurlを読み込む
  var url = location.href;
  navigator.clipboard.writeText(url);
  //アラートの表示
  var completionMessage = 'クリップボードにコピーしました！';
  alert(completionMessage);
}