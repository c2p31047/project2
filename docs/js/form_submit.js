$(function(){
	$('form').on("submit",function(event){//formタグ上でのsubmitイベントを処理(HTML上でformは1つのみが前提)
		event.preventDefault(); //formタグの働きによるsubmitを抑制
		let form = $(this);
		// 送信ボタンを取得（後で使う: 二重送信を防止する。）
		let button = form.find('submit_btn');
		let url = form.attr('action');
		$.ajax({
			url: url, //<form>タグのaction属性の値を利用する
			type: form.attr('method'), //<form>タグのmethod属性の値を利用する
			data: form.serialize(), //formタグの中身を送信可能なオブジェクトに変換
			timeout: 10000, //送信時に失敗まで待つタイムアウトまでの時間(ミリ秒)
			dataType: 'text', //送受信するデータのタイプ
			crossDomain: true,
			// 送信前
			beforeSend: function(xhr, settings) {
				// ボタンを無効化し、二重送信を防止
				button.attr('disabled', true);
			},
			// 応答後
			complete: function(xhr, textStatus) {
				// ボタンを有効化し、再送信を許可
				button.attr('disabled', false);
			},
						
			// 通信成功時の処理
			success: function(result, textStatus, xhr) {
				// 入力値を初期化
				form[0].reset();
				
				let res_obj = $.parseJSON(result);
				alert("ステータス："+res_obj.Status+"\nメッセージ："+res_obj.Message);

				location.reload();

			},
			
			// 通信失敗時の処理
			error: function(xhr, textStatus, error) {
				let err = "送信に失敗しました。\n"+error;
				alert(err);
			}
		});
	});
});
