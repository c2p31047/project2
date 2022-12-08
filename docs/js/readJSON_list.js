$(function(){
	$("main").ready(function(){

		//呼び出された際のURLパラメータの解析（.../list.html?id=1などのとき，変数名idの値(1)を取り出す）
		$.urlParam = function(name){
			var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
			if(results != null){
				return results[1] || 0;
			}
			else{
				return 0;
			}
		}

		const detail_html = "page_detail.html"; //個別詳細形式のページのHTMLファイル

		//const json_url = "https://athena.abe-lab.jp/~hidenao/ProA_2022/Project2_example/data.json";
		// data.jsonでの動作が確認できたら，↑の行をコメント（//を先頭に付ける）して，↓の行のコメント//を外す
		//const json_url = "https://infosys-projecta-2022.github.io/2022-project2-各チームの記号(A～T)/data.json";
		const json_url = "https://raw.githubusercontent.com/c2p31047/project2/main/docs/data.json";

		let q = $.urlParam('q'); //?q=検索語で指定されたとき
		q = decodeURI(q); //URLエンコードされた文字列をスクリプトのコードによる文字列に戻す
		let category = $.urlParam('category'); //?category=カテゴリ名で指定されたとき
		category = decodeURI(category); //URLエンコードされた文字列をスクリプトのコードによる文字列に戻す
		//qやcategoryなどでの検索する場合は，以下の表示HTML作成の処理にif文を追加する
		//[カテゴリごとのページや検索の実行を行うページを実現するためには，list_example.htmlとreadJSON_list.jsをペアで複製する]

		$("#list_container_row").html("");

		$.getJSON(json_url,function(data){ //json_urlで読み出せるJSONデータ(data)の処理を行う
			let num=0; //項目の数を数える
			$.each(data.introduction_obj_list, function(index,elem){ //JSONデータから繰り返し内容部分のHTMLを繰り返し生成

				let item_html='';

				//?q=検索語 を付けてelemの要素を検索する場合は，下記のif文を入れる（item_htmlの生成の文を囲む）
				if(q == 0 || (q != 0 && elem.title.indexOf(q) != -1)) { //?q=が無いときはq==0，?q=があるとき(q!=0)はelemの要素（title, abstract, detailなど）にマッチ
				item_html += '<div class="col">';
				item_html += '<div class="card shadow-sm">';
				item_html += '<a href="'+detail_html+'?id='+elem.id+'" class="card-link" style="text-decoration:none;">';
				item_html += '<img class="bd-placeholder-img card-img-top" src="photos/'+elem.image_file+'_thum.jpg" alt="'+elem.title+'の画像">'; 
				item_html += '<div class="card-body">';
				item_html += '<h2 class="mt-0 text-muted">'+elem.title+'</h2>';
				item_html += '<p class="card-text text-muted">'+elem.abstract+'</p>';
				item_html += '<div class="d-flex justify-content-between align-items-center">';
				item_html += '<div class="btn-group">';
				item_html += '</div>';
				item_html += '<p class="text-muted">'+elem.dtime+'</p>';
				item_html += '</div>';
				item_html += '</div>';
				item_html += '</a>';
				item_html += '</div>';
				item_html += '</div>';
				} //if(elem.title.indexOf(q) != -1) {の終わり（先頭の//だけ消す）
				//”item_htmlの生成の文”はここまで

				$("#list_container_row").append(item_html);//生成したHTMLを<div id="main_content">～</div>間に追加

				num++;
			});
		})
		.fail(function(jqXHR, textStatus, errorThrown) { //urlにアクセスできなかった時のエラー処理
	    	alert("エラー：" + textStatus+"\nreadJSON_list.jsの中のjson_urlの値，または，JSONファイルの内容を確認してください．"+json_url);
		});
	});
});
