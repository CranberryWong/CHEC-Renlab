$(document).ready(function() {

    // var today = new Date();
    // $("#title-date-week").text(moment(today, "YYYY.MM.DD").day(1).format("MMMM DD") + " - " + moment(today, "YYYY.MM.DD").day(7).format("MMMM DD"));
    
    $('.comment-content, .reply-comment-content, .activity-name-data').each(function(){
        $(this).html($(this).text())
    })

    $('.like-count').each(function() {
        if (parseInt($(this).find('.number').attr('data-like-number')) > 0) {
            $(this).show();
            var id = $(this).find(".number").attr("data-id");
            if($(".delete-like-form-" + id)[0]){
                $(this).removeClass("bg-darkgray");
                $(this).addClass("bg-blue");
            }
        } else {
            $(this).hide();
        }
    })

    // show pop up add reflection on friday
    var todayday = new Date().getDay()
    //if friday
    if(todayday == 5){
        if($(".add-reflection-btn").length !=0 && $("#newreflectionmodal").length != 0){
            //show popup reflection
            $('#newreflectionmodal').modal('show');
        }
    }

    //Choose project select2 function
    $(".select2-project-name").select2({
        placeholder: "Choose Project",
        tags: true,
        width: '100%'
    });

    //Choose project group select2 function
    $(".select2-choose-project-group").select2({
        placeholder: "Choose Project Group",
        width: '100%'
    })

    //Choose date range in admin function
    $("#admin-month-picker").datetimepicker({
        viewMode: 'months',
        format: 'MMMM YYYY',
        locale: 'en',
        defaultDate: new Date($("#admin-month-picker").attr('data-month'))
    })

    //onclick the month on admin
    $("#admin-month-picker").on("dp.change", function(e) {
        $("#form-choose-admin-month").submit();
    })

    $(".date-range-datepicker").each(function(){
        //Choose date range datepicker function
        var value = ''; 
        if($(this).val() != ''){
            value = $(this).val()
        } else {
            if ($(this).attr("data-week")==1){
                var firstDate = moment().day(1).format("YYYY.MM.DD");
                var lastDate = moment().day(7).format("YYYY.MM.DD");
                value = "" + firstDate + " - " + lastDate;
            } else
            if ($(this).attr("data-week")==2){
                var firstDate = moment().add(7, 'days').day(1).format("YYYY.MM.DD");
                var lastDate = moment().add(7, 'days').day(7).format("YYYY.MM.DD");
                value = "" + firstDate + " - " + lastDate;
            }
        }
        $(this).datetimepicker({
            format: 'YYYY.MM.DD',
            locale: moment.locale('en', {
                week: { dow: 1 }
            })
        }).on('dp.change', function(e) {
            //Get the value of Start and End of Week
            var val = $(this).val();
            var firstDate = moment(val, "YYYY.MM.DD").day(1).format("YYYY.MM.DD");
            var lastDate = moment(val, "YYYY.MM.DD").day(7).format("YYYY.MM.DD");
            $(this).val(firstDate + " - " + lastDate);
        }).on('dp.hide', function(e){
            if($(this).val() != ''){
                var val = $(this).val()
                var firstDate = moment(val, "YYYY.MM.DD").day(1).format("YYYY.MM.DD");
                var lastDate = moment(val, "YYYY.MM.DD").day(7).format("YYYY.MM.DD");
                $(this).val(firstDate + " - " + lastDate);
            }
        }).on('dp.show',function(e){
            if($(this).val() != ''){
                var val = $(this).val()
                var firstDate = moment(val, "YYYY.MM.DD").day(1).format("YYYY.MM.DD");
                var lastDate = moment(val, "YYYY.MM.DD").day(7).format("YYYY.MM.DD");
                $(this).val(firstDate + " - " + lastDate);
            }
        });
        $(this).val(value);
    });

    // $(document).click(function(e) {
    //     if (($(e.target).closest(".editable-report").length != 0)) {
    //         alert("Clicked outside!");
    //     }
    // });

    $(document).on("click tap",".editactivitybutton", function(e){
        $(this).closest(".editable-report").find(".edit-activity-data").addClass("d-none");
        $(this).closest(".editable-report").find(".edit-activity-input").removeClass("d-none");
        $(this).closest(".editable-report").find("td:last").addClass("d-none");
    })

    // $(".editable-report").each(function(){
    //     $(this).find("td").on('click tap', function(e){
    //         $(this).closest('tr').find('[data-type="text"]').html('<input type="text" name="newactivityname" class="form-control" placeholder="Add Activity..." aria-placeholder="Add Activity..." value="'+$(this).closest('tr').find('[data-type="text"]').attr("data-value")+'">')
            
    //         $(this).closest('tr').find('[data-type="datepicker"]').html('<input type="text" name="newdaterange" placeholder="Date Range" class="form-control col-md-12 date-range-datepicker" data-week="1"/>')
    //         $(this).closest('tr').find('[data-type="datepicker"]').find('input').datetimepicker({
    //             format: 'YYYY.MM.DD',
    //             locale: moment.locale('en', {
    //                 week: { dow: 1 }
    //             })
    //         }).on('dp.change', function(e) {
    //             //Get the value of Start and End of Week
    //             var val = $(this).val();
    //             var firstDate = moment(val, "YYYY.MM.DD").day(1).format("YYYY.MM.DD");
    //             var lastDate = moment(val, "YYYY.MM.DD").day(7).format("YYYY.MM.DD");
    //             $(this).val(firstDate + " - " + lastDate);
    //         });
    //         $(this).closest('tr').find('[data-type="datepicker"]').find('input').val($(this).closest('tr').find('[data-type="datepicker"]').attr("data-value"));

    //         $(this).closest('tr').find('[data-type="select"]').html('<select class="form-control" name="newpriority"><option value="0" disabled hidden>Priority</option><option value="1"> P1</option><option value="2"> P2</option><option value="3"> P3</option></select>')
    //         $(this).closest('tr').find('[data-type="select"]').find("select").val($(this).closest('tr').find('[data-type="select"]').attr("data-value"))

    //         $(this).closest('tr').find('[data-type="number"').html('<span class="input-percentage "><input type="number" name="newpercentage" min="0" max="100" placeholder="Enter ...%" aria-placeholder="Enter ...%" value="'+$(this).closest('tr').find('[data-type="number"').attr("data-value")+'"></span>')

    //         if ($(this).attr("data-type")=="text"){
    //             if($(this).find('input').is(':focus')) return this;
    //             // $(this).html('<input type="text" name="newactivityname" class="form-control" placeholder="Add Activity..." aria-placeholder="Add Activity..." value="'+$(this).attr("data-value")+'">').find('input').trigger('focus')
    //             $(this).find('input').trigger('focus')
    //         } else
    //         if ($(this).attr("data-type") == "datepicker"){
    //             if($(this).find('input').is(':focus')) return this;
    //             // $(this).html('<input type="text" name="newdaterange" placeholder="Date Range" class="form-control col-md-12 date-range-datepicker" data-week="1"/>').find('input').trigger('focus')
    //             $(this).find('input').trigger('focus')
    //         } else
    //         if ($(this).attr("data-type") == "select"){
    //             if($(this).find('select').is(':focus')) return this;
    //             // $(this).html('<select class="form-control" name="newpriority"><option value="0" disabled hidden>Priority</option><option value="1"> P1</option><option value="2"> P2</option><option value="3"> P3</option></select>').find('select').trigger('focus')
    //             $(this).find('select').trigger('focus')
    //             // $(this).find("select").val($(this).attr("data-value"))
    //         } else
    //         if($(this).attr("data-type") == "number"){
    //             if($(this).find('input').is(':focus')) return this;
    //             // $(this).html('<span class="input-percentage "><input type="number" name="newpercentage" min="0" max="100" placeholder="Enter ...%" aria-placeholder="Enter ...%" value="'+$(this).attr("data-value")+'"></span>').find('input').trigger('focus')
    //             $(this).find('input').trigger('focus')
    //         }
    //         $(this).closest('tr').find('td:last').html("<button type='submit' class='btn btn-primary'>SUBMIT</button>")
    //     });
    // })

     //Choose date range datepicker function
     $(".modal-date-range-datepicker").datetimepicker({
        format: 'YYYY.MM.DD',
        locale: moment.locale('en', {
            week: { dow: 1 }
        })
    })

    //Get the value of Start and End of Week
    $('.modal-date-range-datepicker').on('dp.change', function(e) {
        var value = $(".modal-date-range-datepicker").val();
        var firstDate = moment(value, "YYYY.MM.DD").day(1).format("YYYY.MM.DD");
        var lastDate = moment(value, "YYYY.MM.DD").day(7).format("YYYY.MM.DD");
        $(".modal-date-range-datepicker").val(firstDate + " - " + lastDate);
    });


    $(".addbutton").each(function(){
        $(this).prev().hide()
    }).on('click',function(e){
        $(this).prev().toggle()
    })

    $(".deleteactivitybutton").on("click tap",function(e){
        e.preventDefault();
        if(confirm("Are you sure you want to delete this Activity?")){-
            $(".formdeleteactivity-"+$(this).attr("data-id")).submit();
        }
    })

    $(".delete-comment").on("click tap",function(e){
        e.preventDefault();
        if(confirm("Are you sure you want to delete this Comment?")){-
            $(".formdeletecomment-"+$(this).attr("data-id")).submit();
        }
    })

    $(".delete-reply").on("click tap",function(e){
        e.preventDefault();
        if(confirm("Are you sure you want to delete this Reply?")){-
            $(".formdeletereply-"+$(this).attr("data-id")).submit();
        }
    })

    //click the notification function
    $(document).on("click tap", ".read-notif", function(e){
        var classname=$(this).attr("class")
        var n = classname.lastIndexOf('-');
        var id = classname.substring(n + 1);
        $(".readnotificationform-" + id).submit()
    })

    //turn on the tooltip from bootstrap
    $('[data-toggle="tooltip"]').tooltip();

    //like icon and number
    $(document).on("click tap", ".like-count", function(e) {
        var id = $(this).find('.number').attr('data-id')
        if($(".delete-like-form-" + id)[0]){
            $(".delete-like-form-" + id).find("button").click()
        }
        if ($(".add-like-form-" + id)[0]){
            $(".add-like-form-" + id).find("button").click()
        }
        // var id = $(this).parent().find('.number').attr('data-id');
        // var currentCount = parseInt($(this).parent().find('.number').attr('data-like-number'));
        // var hasLike = $(this).parent().find('.number').attr('data-has-like');
        // var newCount, newHasLike;
        // if (hasLike == 0) {
        //     newCount = currentCount + 1;
        //     newHasLike = 1;
        // } else {
        //     newCount = currentCount - 1;
        //     newHasLike = 0;
        // }
        // $(this).parent().find('.number').attr('data-has-like', newHasLike);
        // $(this).parent().find('.number').attr('data-like-number', newCount);
        // $(this).parent().find('.number').html(newCount);
        // $(this).parent().find('.like-comment[data-id="' + id + '"').attr('data-has-like', newHasLike);
        // if (newCount > 0) {
        //     $(this).show();
        // } else {
        //     $(this).hide();
        // }
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
        // $(this).closest('.media-body').append('<div class = "mt-3 media position-relative"><img src = "https://chec-static.s3.amazonaws.com/members/Fitra%20Rahmamuliani/avatar.png?AWSAccessKeyId=AKIAJMTKKG3VUAMWLACA&Signature=c%2FZGb31S1VjB1IXO96hsQe4MHdg%3D&Expires=1597732227" alt = "Avatar" class = "mr-3 rounded-circle comment-photo" /> <div class = "media-body align-self-center"> <form class = "d-flex flex-row mb-0 reply-comment-form" id="reply-form"><input type = "text" class = "form-control flex-grow-1 reply-comment-input" placeholder = "Write a reply..." /> <button type = "button" class = "btn btn-primary ml-2 reply-comment-submit" > COMMENT </button> </form> </div> </div>');
        if($(this).closest('.top-comment-section').find('.reply-form-div').hasClass('d-none')){   
            $(this).closest('.top-comment-section').find('.reply-form-div').removeClass('d-none');
        }
        $(this).closest('.top-comment-section').find('.reply-form-div').find('.reply-comment-input').focus();
        $(this).closest('.top-comment-section').find('.reply-form-div').find('.reply-comment-input').suggest('@', {
            data: memberList,
            map: function(user) {
                return {
                    value: user.text,
                    text: '<strong>' + user.text + '</strong>'
                }
            }
        });
    });

    var memberList = [
        { id: 14, text: "Xinhui Jiang" },
        { id: 15, text: "Yang Li" },
        { id: 16, text: "Chen Wang" },
        { id: 19, text: "Yilin Zheng" },
        { id: 20, text: "Chunyuan Lan" },
        { id: 28, text: "Xiaofei Zhu" },
        { id: 29, text: "Junlin Sun" },
        { id: 21, text: "Xinpeng Li" },
        { id: 22, text: "Xi Chen" },
        { id: 23, text: "Sai Jiang" },
        { id: 24, text: "Hongyun Lyu" },
        { id: 25, text: "Jian Zhang" },
        { id: 26, text: "Zhihang Guo" },
        { id: 27, text: "Yanyin Zhou" },
        { id: 30, text: "Akinori Kondo" },
        { id: 31, text: "Hijiri Kaneko" },
        { id: 32, text: "Ryota Torii" },
        { id: 33, text: "Takaaki Kubo" },
        { id: 34, text: "Yusuke Tokito" },
        { id: 35, text: "Saki Hiramatsu" },
        { id: 36, text: "Jiayuan Geng" },
        { id: 37, text: "Adachi Kenshi" },
        { id: 38, text: "Miyamoto Daisuke" },
        { id: 1, text: "Fitra Rahmamuliani" },
        { id: 18, text: "Xiaoxuan Li" },
        { id: 0, text: "Xiangshi Ren" },
        { id: 17, text: "Kiyoshi Nakahara" },
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
        { id: 13, text: "Kyoko Hatakenaka" },
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

    $('.reply-comment-input').suggest('@', {
        data: memberList,
        map: function(user) {
            return {
                value: user.text,
                text: '<strong>' + user.text + '</strong>'
            }
        }
    });

    // $(document).on("keypress", ".reply-comment-input", function(e) {
    //     if (e.which == 13) {
    //         e.preventDefault();
    //         var inputVal = $(this).val();
    //         $(".reply-comment-submit").click();
    //     }
    // });

    // $(document).on("submit", "#reply-form", function(e) {
    //     e.preventDefault();
    // })

    // $(document).on("click", ".reply-comment-submit", function(e) {
    //     var newId = parseInt($(this).parents().siblings('.comment-section').find('.like-comment').attr('data-id')) + 1;

    //     $(this).parents().siblings('.comment-section').append('<div class="media position-relative reply-comment-section w-100 mt-2"> <img src="https://chec-static.s3.amazonaws.com/members/Fitra%20Rahmamuliani/avatar.png?AWSAccessKeyId=AKIAJMTKKG3VUAMWLACA&Signature=c%2FZGb31S1VjB1IXO96hsQe4MHdg%3D&Expires=1597732227" alt="Avatar" class="mr-3 rounded-circle comment-photo" /> <div class="media-body row"> <div class="comment-section col-md-auto"> <div class="rounded shadow-sm p-3"> <b class="commentator">Fitra Rahmamuliani</b><p class="comment-content mb-0 mt-1">' + $(".reply-comment-input").val() + '</p> </div> <div class="like-count rounded align-self-end float-right bg-darkgray text-white py-1 px-2"> <i class="fa fa-thumbs-up mr-2"></i><span class="number" data-id="' + newId + '" data-like-number="0" data-has-like="0">0</span> </div> <div class="d-flex flex-row mx-2 col-md-12"> <button class="btn btn-link text-body like-comment" data-id="' + newId + '" data-has-like="0"><small><b>Like</b></small></button> <button class="btn btn-link text-body ml-4 reply-comment"><small><b>Reply</b></small></button> <span class="text-black-50 align-self-center ml-5"><small>15 seconds ago</small></span> </div> </div> </div> </div>');

    //     $('.like-count').each(function() {
    //         if (parseInt($(this).find('.number').attr('data-like-number')) > 0) {
    //             $(this).show();
    //         } else {
    //             $(this).hide();
    //         }
    //     })
    //     $(".reply-comment-input").val('');
    //     $(".reply-comment-input").focus();
    // });

    $(".notification-icon").popover({
        boundary: 'window',
        html: true,
        content: function() {
            return $(".notification-container").html();
        },
        'placement': 'bottom',
    })

    $(document).on("click", ".edit-comment", function(e){
        $(this).parents(".comment-section").find(".shadow-sm").html('<form class="d-flex flex-row" action="/newblog/editcomment" method="POST"> <input name="newcommenttext" type="text" class="form-control edit-comment-inputtext" value="'+$(this).parents(".comment-section").find(".comment-content").text()+'"/> <input type="hidden" name="newcommentid" value="'+ $(this).attr("data-commentid") +'"/> <button class="btn btn-primary ml-2" type="submit">SUBMIT</button> </form>');
        $(this).parents(".comment-section").find(".shadow-sm").removeClass("shadow-sm");
        $(this).addClass("d-none")
        $('.edit-comment-inputtext').suggest('@', {
            data: memberList,
            map: function(user) {
                return {
                    value: user.text,
                    text: '<strong>' + user.text + '</strong>'
                }
            }
        });
    })

    $(document).on("click", ".edit-reply", function(e){
        $(this).closest(".reply-comment-section").find(".shadow-sm").html('<form class="d-flex flex-row" action="/newblog/editreply" method="POST"> <input name="newreplytext" type="text" class="form-control edit-reply-inputtext" value="'+$(this).closest(".reply-comment-section").find(".reply-comment-content").text()+'"/> <input type="hidden" name="newreplyid" value="'+ $(this).attr("data-replyid") +'"/> <button class="btn btn-primary ml-2" type="submit">SUBMIT</button> </form>');
        $(this).closest(".reply-comment-section").find(".shadow-sm").removeClass("shadow-sm");
        $(this).addClass("d-none")
        
        $('.edit-reply-inputtext').suggest('@', {
            data: memberList,
            map: function(user) {
                return {
                    value: user.text,
                    text: '<strong>' + user.text + '</strong>'
                }
            }
        });
    })

    $('.sort-report-title').click(function(e) {
        e.preventDefault();
        var id = $(this).attr("data-id");
        if ($('.report-table[data-id="' + id + '"]').is(":visible")) {
            $('.report-table[data-id="' + id + '"] .row').sort(function(a, b) {
                return $(a).find(".col-5").text() > $(b).find(".col-5").text() ? 1 : -1;
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
            $('.report-table[data-id="' + id + '"]').find('tr').sort(function(a, b) {
                return $(a).find(".col-3 .edit-activity-data").text() > $(b).find(".col-3 .edit-activity-data") ? 1 : -1;
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
                var result = $(this).find('.activity-name-data').text().toLowerCase().indexOf(filter);
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

    $('.search-activity-title').keypress(function(e) {
        if(e.which == 13 || e.keyCode == 13) {
            e.preventDefault();
        }
    });

    $('.carousel').carousel({
        interval: 0
    })

    // Add the following code if you want the name of the file appear on select
    $(".custom-file-input").on("change", function() {
        var fileName = $(this).val().split("\\").pop();
        $(this).siblings(".custom-file-label").addClass("selected").html(fileName);
        if (this.files && this.files[0]) {
            var reader = new FileReader();

            reader.onload = function(e) {
                $('#edit-profile-photo').attr('src', e.target.result);
            }

            reader.readAsDataURL(this.files[0]);
        }
    });

    var leaderboardtop = document.getElementsByClassName('leaderboardtop')
    var leaderboardbottom = document.getElementsByClassName('leaderboardbottom')

    if(leaderboardtop.length>0){
        $(".topboard").show();
        $(".topboard").on("click",function(){
            $(".leaderboardtop").toggle();
            if($(this).text() == 'Show the top')
            {
                $(this).text('Hide the top');
            }
            else{
                $(this).text('Show the top');
            }
        })
    }
    if (leaderboardbottom.length > 0){
        $(".bottomboard").show();
        $(".bottomboard").on("click",function(){
            $(".leaderboardbottom").toggle();
            if($(this).text() == 'Show the bottom')
            {
                $(this).text('Hide the bottom');
            }
            else{
                $(this).text('Show the bottom');
            }
        })
    }

    //back to top
        $(window).scroll(function () {
                if ($(this).scrollTop() > 50) {
                    $('#back-to-top').fadeIn();
                } else {
                    $('#back-to-top').fadeOut();
                }
            });
            // scroll body to 0px on click
            $('#back-to-top').click(function () {
                $('body,html').animate({
                    scrollTop: 0
                }, 400);
                return false;
            });

});