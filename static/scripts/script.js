$(document).ready(function() {

    var today = new Date();
    $("#title-date-week").text(moment(today, "YYYY.MM.DD").day(1).format("MMMM DD") + " - " + moment(today, "YYYY.MM.DD").day(7).format("MMMM DD"));
    $('.like-count').each(function() {
        if (parseInt($(this).find('.number').attr('data-like-number')) > 0) {
            $(this).show();
        } else {
            $(this).hide();
        }
    })

    //Choose project select2 function
    $(".select2-project-name").select2({
        placeholder: "Choose Project",
        tags: true,
        width: '100%'
    });

    //Choose date range in admin function
    $("#admin-month-picker").datetimepicker({
        viewMode: 'months',
        format: 'MMMM YYYY',
        locale: 'en',
        date: moment()
    })

    //Choose date range datepicker function
    $("#date-range-datepicker").datetimepicker({
        format: 'YYYY.MM.DD',
        locale: moment.locale('en', {
            week: { dow: 1 }
        })
    })

    //Get the value of Start and End of Week
    $('#date-range-datepicker').on('dp.change', function(e) {
        var value = $("#date-range-datepicker").val();
        var firstDate = moment(value, "YYYY.MM.DD").day(1).format("YYYY.MM.DD");
        var lastDate = moment(value, "YYYY.MM.DD").day(7).format("YYYY.MM.DD");
        $("#date-range-datepicker").val(firstDate + " - " + lastDate);
    });

    //turn on the tooltip from bootstrap
    $('[data-toggle="tooltip"]').tooltip();

    //like icon and number
    $(document).on("click tap", ".like-count", function(e) {
        var id = $(this).parent().find('.number').attr('data-id');
        var currentCount = parseInt($(this).parent().find('.number').attr('data-like-number'));
        var hasLike = $(this).parent().find('.number').attr('data-has-like');
        var newCount, newHasLike;
        if (hasLike == 0) {
            newCount = currentCount + 1;
            newHasLike = 1;
        } else {
            newCount = currentCount - 1;
            newHasLike = 0;
        }
        $(this).parent().find('.number').attr('data-has-like', newHasLike);
        $(this).parent().find('.number').attr('data-like-number', newCount);
        $(this).parent().find('.number').html(newCount);
        $(this).parent().find('.like-comment[data-id="' + id + '"').attr('data-has-like', newHasLike);
        if (newCount > 0) {
            $(this).show();
        } else {
            $(this).hide();
        }
    });

    //like button under the comment
    $(document).on("click tap", ".like-comment", function(e) {
        var id = $(this).attr('data-id');
        var hasLike = $(this).attr('data-has-like'); //0: false, 1: true
        var currentCount = parseInt($(this).closest('.media-body').find('.number[data-id="' + id + '"').attr('data-like-number'));
        var newCount, newHasLike;
        if (hasLike == 0) {
            newCount = currentCount + 1;
            newHasLike = 1;
        } else {
            newCount = currentCount - 1;
            newHasLike = 0;
        }
        $(this).attr('data-has-like', newHasLike);
        $(this).closest('.media-body').find('.number[data-id="' + id + '"').attr('data-has-like', newHasLike);
        $(this).closest('.media-body').find('.number[data-id="' + id + '"').attr('data-like-number', newCount);
        $(this).closest('.media-body').find('.number[data-id="' + id + '"').html(newCount);
        if (newCount > 0) {
            $(this).closest('.media-body').find('.number[data-id="' + id + '"').parent('.like-count').show();
        } else {
            $(this).closest('.media-body').find('.number[data-id="' + id + '"').parent('.like-count').hide();
        }
    });

    //reply form showing up when press reply button
    $('.reply-comment').one('click tap', function() {
        $(this).closest('.media-body').append('<div class = "mt-3 media position-relative"><img src = "https://images.unsplash.com/photo-1554080353-a576cf803bda?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80" alt = "Fitra Rahmamuliani Avatar" class = "mr-3 rounded-circle comment-photo" /> <div class = "media-body align-self-center"> <form class = "d-flex flex-row mb-0 reply-comment-form" id="reply-form"><input type = "text" class = "form-control flex-grow-1 reply-comment-input" placeholder = "Write a reply..." /> <button type = "button" class = "btn btn-primary ml-2 reply-comment-submit" > COMMENT </button> </form> </div> </div>');
        $('.reply-comment-input').focus();
        $('.reply-comment-input').suggest('@', {
            data: memberList,
            map: function(user) {
                return {
                    value: user.name,
                    text: '<strong>' + user.name + '</strong>'
                }
            }
        });
    });

    var memberList = [
        { id: 0, text: "Xiangshi Ren" },
        { id: 1, text: "Kiyoshi Nakahara" },
        { id: 2, text: "Kaechang Park" },
        { id: 3, text: "Yukinobu Hoshino" },
        { id: 4, text: "Kazunori Ueda" },
        { id: 5, text: "Toru Kurihara" },
        { id: 6, text: "Kavous Salehzadeh Niksirat" },
        { id: 7, text: "Silpasuwanchai Chaklam" },
        { id: 8, text: "Kibum Kim" },
        { id: 9, text: "Zhenxin Wang" },
        { id: 10, text: "Sayan Sarcar" },
        { id: 11, text: "William Delamare" },
        { id: 12, text: "Hamed Aliyari" },
        { id: 13, text: "Kyoko Hatakenaka" },
        { id: 14, text: "Xinhui Jiang" },
        { id: 15, text: "Yang Li" },
        { id: 16, text: "Chen Wang" },
        { id: 17, text: "Fitra Rahmamuliani" },
        { id: 18, text: "Xiaoxuan Li" },
        { id: 19, text: "Yilin Zheng" },
        { id: 20, text: "Chunyuan Lan" },
        { id: 21, text: "Xinpeng Li" },
        { id: 22, text: "Xi Chen" },
        { id: 23, text: "Sai Jiang" },
        { id: 24, text: "Hongyun Lyu" },
        { id: 25, text: "Jian Zhang" },
        { id: 26, text: "Zhihang Guo" },
        { id: 27, text: "Yanyin Zhou" },
        { id: 28, text: "Xiaofei Zhu" },
        { id: 29, text: "Junlin Sun" },
        { id: 30, text: "Akinori Kondo" },
        { id: 31, text: "Hijiri Kaneko" },
        { id: 32, text: "Ryota Torii" },
        { id: 33, text: "Takaaki Kubo" },
        { id: 34, text: "Yusuke Tokito" },
        { id: 35, text: "Saki Hiramatsu" },
        { id: 36, text: "Jiayuan Geng" },
        { id: 37, text: "Adachi Kenshi" },
        { id: 38, text: "Miyamoto Daisuke" }
    ];

    $("#select-project-member").select2({
        placeholder: "Enter member's name...",
        data: memberList,
        width: '100%'
    });

    $('.input-comment').suggest('@', {
        data: memberList,
        map: function(user) {
            return {
                value: user.text,
                text: '<strong>' + user.text + '</strong>'
            }
        }
    });

    $(document).on("keypress", ".reply-comment-input", function(e) {
        if (e.which == 13) {
            e.preventDefault();
            var inputVal = $(this).val();
            $(".reply-comment-submit").click();
        }
    });

    $(document).on("submit", "#reply-form", function(e) {
        e.preventDefault();
    })

    $(document).on("click", ".reply-comment-submit", function(e) {
        var newId = parseInt($(this).parents().siblings('.comment-section').find('.like-comment').attr('data-id')) + 1;

        $(this).parents().siblings('.comment-section').append('<div class="media position-relative reply-comment-section"> <img src="https://images.unsplash.com/photo-1554080353-a576cf803bda?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80" alt="Zhihang Guo Avatar" class="mr-3 rounded-circle comment-photo" /> <div class="media-body"> <div class="comment-section"> <div class="rounded shadow p-3"> <b class="commentator">Fitra Rahmamuliani</b><p class="comment-content mb-0 mt-1">' + $(".reply-comment-input").val() + '</p> </div> <div class="like-count rounded float-right bg-darkgray text-white py-1 px-2"> <i class="fa fa-thumbs-up mr-2"></i><span class="number" data-id="' + newId + '" data-like-number="0" data-has-like="0">0</span> </div> <div class="d-flex flex-row mx-2"> <button class="btn btn-link text-body like-comment" data-id="' + newId + '" data-has-like="0"><small><b>Like</b></small></button> <button class="btn btn-link text-body ml-4 reply-comment"><small><b>Reply</b></small></button> <span class="text-black-50 align-self-center ml-5"><small>15 seconds ago</small></span> </div> </div> </div> </div>');

        $('.like-count').each(function() {
            if (parseInt($(this).find('.number').attr('data-like-number')) > 0) {
                $(this).show();
            } else {
                $(this).hide();
            }
        })
        $(".reply-comment-input").val('');
        $(".reply-comment-input").focus();
    });

    $(".notification-icon").popover({
        boundary: 'window',
        html: true,
        content: function() {
            return $(".notification-container").html();
        },
        'placement': 'bottom',
    })

    $('.sort-report-title').click(function(e) {
        e.preventDefault();
        var id = $(this).attr("data-id");
        if ($('.report-table[data-id="' + id + '"]').is(":visible")) {
            $('.report-table[data-id="' + id + '"] .row').sort(function(a, b) {
                return $(a).find(".col-6").text() > $(b).find(".col-6").text() ? 1 : -1;
            }).appendTo('.report-table[data-id="' + id + '"]');
        } else {
            $('.card-report[data-id="' + id + '"] .card').sort(function(a, b) {
                return $(a).find(".card-title").text() > $(b).find(".card-title").text() ? 1 : -1;
            }).appendTo('.card-report[data-id="' + id + '"]');
        }

    })

    $('.sort-report-date').click(function(e) {
        e.preventDefault();
        var id = $(this).attr("data-id");
        if ($('.report-table[data-id="' + id + '"]').is(":visible")) {
            $('.report-table[data-id="' + id + '"] .row').sort(function(a, b) {
                return $(a).find(".col-3").text() > $(b).find(".col-3").text() ? 1 : -1;
            }).appendTo('.report-table[data-id="' + id + '"]');
        } else {
            $('.card-report[data-id="' + id + '"] .card').sort(function(a, b) {
                return $(a).find(".card-date").text() > $(b).find(".card-date").text() ? 1 : -1;
            }).appendTo('.card-report[data-id="' + id + '"]');
        }

    })

    $('.sort-report-priority').click(function(e) {
        e.preventDefault();
        var id = $(this).attr("data-id");
        if ($('.report-table[data-id="' + id + '"]').is(":visible")) {
            $('.report-table[data-id="' + id + '"] .row').sort(function(a, b) {
                return $(a).find(".priority").text() > $(b).find(".priority").text() ? 1 : -1;
            }).appendTo('.report-table[data-id="' + id + '"]');
        } else {
            $('.card-report[data-id="' + id + '"] .card').sort(function(a, b) {
                return $(a).find(".priority").text() > $(b).find(".priority").text() ? 1 : -1;
            }).appendTo('.card-report[data-id="' + id + '"]');
        }
    })


    $('.sort-report-progress').click(function(e) {
        e.preventDefault();
        var id = $(this).attr("data-id");
        if ($('.report-table[data-id="' + id + '"]').is(":visible")) {
            $('.report-table[data-id="' + id + '"] .row').sort(function(a, b) {
                return parseInt($(a).find(".report-progress").attr("data-progress")) - parseInt($(b).find(".report-progress").attr("data-progress"));
            }).appendTo('.report-table[data-id="' + id + '"]');
        } else {
            $('.card-report[data-id="' + id + '"] .card').sort(function(a, b) {
                return parseInt($(a).find(".report-progress").attr("data-progress")) - parseInt($(b).find(".report-progress").attr("data-progress"));
            }).appendTo('.card-report[data-id="' + id + '"]');
        }
    })

    $('.search-activity-title').keyup(function(e) {
        var id = $(this).attr("data-id");
        var filter = $(this).val().toLowerCase(); // get the value of the input, which we filter on
        if ($('.report-table[data-id="' + id + '"]').is(":visible")) {
            $('.row').removeClass('d-none');
            $('.report-table[data-id="' + id + '"] .row').filter(function() {
                var result = $(this).find('.col-6').text().toLowerCase().indexOf(filter);
                $(this).toggle(result > -1);
            });
        } else {
            $('.card').removeClass('d-none');
            $('.card-report[data-id="' + id + '"] .card').filter(function() {
                $(this).toggle($(this).find('.card-body h5').text().toLowerCase().indexOf(filter) > -1);
            });
            // $('.card-report').find('.card .card-body h5:not(:contains("' + filter + '"))').parent().parent().addClass('d-none');
            e.preventDefault();

        }
    })


});