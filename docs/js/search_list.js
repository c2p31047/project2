$(function(){
	$("main").ready(function(){

        $('#search_btn').on('click',function(){
            let keyword = $('#search_keyword').val();//id=search_keywordのinputタグからキーワードを取得

            //readJSON_list.jsを含むリスト形式の検索を表示するhtmlファイル←list_example.htmlから作成する検索結果表示用htmlファイル
            //（検索結果を別の表示にする場合は，一覧形式のhtmlとreadJSON_list.jsとペアで複製する）
            //let search_url = "https://athena.abe-lab.jp/~hidenao/ProA_2022/Project2_example/list_example.html";
            //let search_url = "https://infosys-projecta-2022.github.io/2022-project2-グループ記号[A-T]/list_example.html";
            let search_url = "https://infosys-projecta-2022.github.io/2022-project2-f/page_list.html";
            
            search_url +='?q='+keyword;//キーワードをURLに追加
            search_url = encodeURI(search_url); //URLエンコードを行い
            location.href = search_url; //検索機能の付いたhtmlとreadJSON_list.jsのコピーのペアに結果を表示させる
        });

	});
});
