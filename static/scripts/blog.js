function contentRequest (title, id) {
    console.log("here?");
    var jqxhr = $.ajax('/blogcontent?title=' + title, {
        method: 'get',    
    }).done(function (data) {
        console.log('成功, 收到的数据: ');
        $('#'+id).children().first().html(data)
    }).fail(function (xhr, status) {
        console.log('失败: ' + xhr.status + ', 原因: ' + status);
    }).always(function () {
        console.log('请求完成: 无论成功或失败都会调用');
    });
}

