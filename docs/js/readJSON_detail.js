$(function(){
	$("#main_content").ready(function(){

		//呼び出された際のURLパラメータの解析（.../detail1.html?id=1などのとき，変数名idの値(1)を取り出す）※テンプレートの時点では使っていない
		$.urlParam = function(name){
			let results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
			if(results != null){
				return results[1] || 0;
			}
			else{
				return 0;
			}
		}

		//const json_url = "https://athena.abe-lab.jp/~hidenao/ProA_2022/Project2_example/data.json";
		// data.jsonでの動作が確認できたら，↑の行をコメント（//を先頭に付ける）して，↓の行のコメント//を外す
		//const json_url = "https://infosys-projecta-2022.github.io/2022-project2-f/data.json";
		const json_url = "https://raw.githubusercontent.com/c2p31047/project2/main/docs/data.json";


		let id = 0; 
		if(id == 0){
			id = $.urlParam('id'); //?id=Nで指定されたとき
		}

		$.getJSON(json_url,function(data){ //urlの文字列のURLからidまたはqで指定した値を持つJSONオブジェクトを取得

			const obj_list = data.introduction_obj_list;
			const obj = obj_list.find( element => element.id == id); //対象の１つ（一行）をオブジェクトとしてJSONから取り出す

			if(obj === undefined){
				alert('idの値は'+json_url+'のJSONデータ内にあるidの値としてください．');
				return false;
			}

			if($("main").get(0)){ //<main>～</main>があったら

				$("head > title").text(obj.title); //<head><title>～</title></head>の間の～のところ（文字列）を変更
				$("#top-title").text(obj.title); //ページの一番上の見出しの<div id="top-title">ところ（文字列）を変更
				$("#top-abstract").text(obj.abstract); //ページの一番上の見出しの<div id="top-abstract">ところ（文字列）を変更
				if($("h2").get(0)){ //<h2>のタグがあったら(すべてのh2タグが変更されるので，必要に応じてidで区別する)
					$("h2").text(obj.title);
				}

				//<img id="thumnail_img">タグのsrcの値をサムネイル画像のファイルに設定（photosフォルダに”画像名_thum.jpg”がある必要がある）
				$("img#thumnail_img").attr("src","./photos/"+obj.image_file+"_thum.jpg");

				if($("p#abstract").get(0)){ //<p id="abstract"></p>のタグがあったら
					$("p#abstract").text(obj.abstract); //abstract（DBではカラム）の値を変更
				}

				if($("p#detail").get(0)){//<p id="detail"></p>のタグがあったら
					$("p#detail").html(obj.detail); //detail（DBではカラム）の値を変更
				}

                                //[ここから追加した項目]====================================================

				if($("p#bone").get(0)){ //<p id="bone"></p>のタグがあったら
					$("p#bone").html(obj.bone); //bone（DBではカラム）の値を変更
				}

				if($("p#btwo").get(0)){ //<p id="btwo"></p>のタグがあったら
					$("p#btwo").html(obj.btwo); //btwo（DBではカラム）の値を変更
				}

				if($("p#bthree").get(0)){ //<p id="bthree"></p>のタグがあったら
					$("p#bthree").html(obj.bthree); //bthree（DBではカラム）の値を変更
				}

				if($("p#bfour").get(0)){ //<p id="bfour"></p>のタグがあったら
					$("p#bfour").html(obj.bfour); //bfour（DBではカラム）の値を変更
				}

				if($("p#bfive").get(0)){ //<p id="bfive"></p>のタグがあったら
					$("p#bfive").html(obj.bfive); //bfive（DBではカラム）の値を変更
				}

				if($("p#bsix").get(0)){ //<p id="bsix"></p>のタグがあったら
					$("p#bsix").html(obj.bsix); //bsix（DBではカラム）の値を変更
				}

				if($("p#bsev").get(0)){ //<p id="bsev"></p>のタグがあったら
					$("p#bsev").html(obj.bsev); //bsev（DBではカラム）の値を変更
				}

				//リンク用
				if($("p#link").get(0)){ //<p id="link"></p>のタグがあったら
					$("p#link").html(obj.link); //link（DBではカラム）の値を変更
				}
				if($("p#linkSec").get(0)){ //<p id="linkSec"></p>のタグがあったら
					$("p#linkSec").html(obj.linkSec); //linkSec（DBではカラム）の値を変更
				}

				//データ更新日
				if($("p#dtime").get(0)){ //<p id="dtime"></p>のタグがあったら
					$("p#dtime").html(obj.dtime); //dtime（DBではカラム）の値を変更
				}


                                //ここまで====================================================

				if($("#image_list").get(0)){//<div id="image_list">のタグがあったら
					$("#image_list").html(""); //id=image_listのタグの中のHTMLを空にする
					let img_tag = "";

					//各画像ファイルを「追加の画像」としてlightbox2のリストとして<img>タグを追加していく
					if(obj.image_file1 != null && obj.image_file1!=""){
						img_tag += '<a href="./photos/'+obj.image_file1+'.jpg" data-lightbox="image-list">';
						img_tag += '<img src="./photos/'+obj.image_file1+'_thum.jpg" class="col-3 mb-5 box-shadow"/></a>';
					}

					if(obj.image_file2 != null && obj.image_file2!=""){
						img_tag += '<a href="./photos/'+obj.image_file2+'.jpg" data-lightbox="image-list">';
						img_tag += '<img src="./photos/'+obj.image_file2+'_thum.jpg" class="col-3 mb-5 box-shadow"/></a>';
					}

					if(obj.image_file3 != null && obj.image_file3!=""){
						img_tag += '<a href="./photos/'+obj.image_file3+'.jpg" data-lightbox="image-list">';
						img_tag += '<img src="./photos/'+obj.image_file3+'_thum.jpg" class="col-3 mb-5 box-shadow"/></a>';
					}

					$("#image_list").append(img_tag); //id=image_listのタグにリンク付きの<img>タグを追加する

 				}

				if($("div.star-rating").get(0)){//<div class="star-rating">のタグがあったら，scoreの値によって黄色い☆の表示幅を変更する
					if(obj.score != null){
						const font_size_str = $("div.star-rating").css("font-size");
						const font_size = font_size_str.match(/\d+/)[0]; //○○pxの○○（数字の部分を抜き出す）
						const width = (obj.score / 5.0) *font_size*5; //px値にする(5は満点)
					  $("div.star-rating-front").attr("style","width: "+width+"px"); //scoreの値をstar-rating-frontのstyle="width: ○○%"の値とする
					}
				}

				if($("#map_here").get(0)){//<div id="map_here">のタグがあったら
					//leaflet.jsを使ってOpen Street Mapを表示する
					// 地図のデフォルトの緯度経度(35.369744, 139.415493)と拡大率(拡大レベル16)
					let map = L.map('map_here').setView([obj.lat, obj.lng], 16);//map_hereはidの値
 
					// 描画する(Copyrightは消してはならない)
					L.tileLayer(
						'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', 
						{ attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' }
					).addTo(map);

					//マーカーを地図に追加する
					L.marker([obj.lat, obj.lng]).addTo(map);

				}

			}
			else{
				alert('<main>のタグは消さないでください．');
			}

		})
		.fail(function(jqXHR, textStatus, errorThrown) { //urlにアクセスできなかった時のエラー処理
    		alert("エラー：" + textStatus+"\n以下のURLにアクセスできませんでした．"+json_url);
		});
	});
});


