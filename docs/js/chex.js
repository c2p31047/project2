// アラートを表示する関数
function showAlert(checkboxes) {
  // チェックボックスの数を取得する
  const numCheckboxes = checkboxes.length;

  // チェックされているチェックボックスの数を数える
  let numChecked = 0;
  for (const checkbox of checkboxes) {
    if (checkbox.checked) {
      numChecked += 1;
    }
  }

  // チェックされているチェックボックスの数が
  // チェックボックスの数と同じ場合、すべてのチェックボックスが
  // チェックされていると見なす
  if (numChecked === numCheckboxes) {
    alert('すべてのチェックボックスがチェックされました！');
  }
}

// class 属性が "chak" の div 要素を取得する
const divs = document.querySelectorAll('div.chak');

// div 要素ごとに処理をする
for (const div of divs) {
  // div 要素内のチェックボックスを取得する
  const checkboxes = div.querySelectorAll('input[type="checkbox"]');

  // チェックボックスがクリックされたときに
  // アラートを表示する関数を実行する
  for (const checkbox of checkboxes) {
    checkbox.addEventListener('click', () => showAlert(checkboxes));
  }
}
