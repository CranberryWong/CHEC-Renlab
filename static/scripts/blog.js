function contentRequest (title, id) {
    var jqxhr = $(this).ajax('/blogcontent?title=' + title, {
        method: 'get',    
    }).done(function (data) {
        ajaxLog('成功, 收到的数据: ');
        $(id).children().first().text(data)
    }).fail(function (xhr, status) {
        ajaxLog('失败: ' + xhr.status + ', 原因: ' + status);
    }).always(function () {
        ajaxLog('请求完成: 无论成功或失败都会调用');
    });
}

