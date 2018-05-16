function contentRequest (title, name, id) {
    console.log("here?");
    var jqxhr = $.ajax('/blogcontent?title=' + title + '&name=' + name, {
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

function profileEditingRequest (url) {
    console.log("Profile Editing");
    var jqxhr = $.ajax(url, {
        method: 'get',
    }).done(function (data) {
        console.log("success!");
        $('.profile-edit').html(
            '<form role="form" action="/profilewriting" method="post">' +
            '<button type="submit" class="btn btn-outline-primary btn-sm" style="margin-bottom:10px;">Done</button>' +
            '<div class="form-group">' +
            '<textarea class="form-control" rows="17" placeholder="" name="content">' +
                data +
            '</textarea>' +
            '</div>' +
            '</form>'
        );
        $('.profile-content').html('');
    }).fail(function (xhr, status) {
        console.log('失败: ' + xhr.status + ', 原因: ' + status);
    }).always(function () {
        console.log('请求完成: 无论成功或失败都会调用');
    });
}

function contentRevise (title) {
    console.log("here?");
    var jqxhr = $.ajax('/blogrevising?title=' + title, {
        method: 'get',    
    }).done(function (data) {
        console.log('成功, 收到的数据: ');
        $('#blog-form-title').val(title)
        $('#blog-form-content').text(data)
    }).fail(function (xhr, status) {
        console.log('失败: ' + xhr.status + ', 原因: ' + status);
    }).always(function () {
        console.log('请求完成: 无论成功或失败都会调用');
    });
}

