$(window).scroll(function () {
    var $nav = $("#sider-menu ul li"),
        length = $nav.length,//获取导航菜单 ul li 的个数
        item = new Array(),//新建一个数组
        sTop = $(window).scrollTop();//获取偏移的高度

    if($("#sider-menu").offset().top <= 580 ){
        $("#sider-menu").offset({top:540});
        
        console.log($("#sider-menu").offset().top)
    } else {
        $("#sider-menu").css("top",20);
        console.log($("#sider-menu").offset().top)
    }

    for (var i = 0; i < length; i++) {
        if (i == 0) {
            item[i + 1] = $(".blockList:first-child").offset().top;
            if (sTop >= item[i + 1]) {
                $nav.eq(i).addClass("active").siblings("li").removeClass("active");//选中的样式selected  

            }
            
        } else {
            item[i + 1] = $(".blockList:nth-child(" + (i + 1) + ")").offset().top;
            if (sTop >= item[i + 1]) {
                $nav.eq(i).addClass("active").siblings("li").removeClass("active");

            }
        }
    }
})