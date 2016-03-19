function modify_table(action, req_data) {
    $.ajax('/modify_table/' + action, {
        type: "POST",
        data: req_data
    });
}

function flash_message(text, category) {
    if (category === 'error') {
        var msg_timeout = 3000;
    } else if (category === 'info') {
        var msg_timeout = 1200;
    }
    var n = noty({
        text: text,
        layout: 'topRight',
        type: category,
        timeout: msg_timeout
    });
}

$(".inputSpan span").click(function() {
    var $this = $(this);
    $this.hide().siblings("input").val($this.text()).show().focus().select();
});

function hideInputshowSpan(e) {
    if (e.val() === '') {
        flash_message('You must enter non-empty value', 'error');
        return;
    }
    e.hide().siblings("span").text(e.val()).show();
    if (e.parent().attr('datalabel') === 'section') {
        modify_table('update_section', {
            new_title: e.val(),
            section_id: e.parent().attr('name')
        });
    } else if (e.parent().attr('datalabel') === 'subsection') {
        modify_table('update_subsection', {
            new_title: e.val(),
            subsection_id: e.parent().attr('name')
        });
    }
}

$(".inputSpan input").blur(function() {
    hideInputshowSpan($(this));

}).hide();

$(".inputSpan input").keyup(function(e) {
    if (e.keyCode == 13) {
        hideInputshowSpan($(this));
    }
});


$(".goal-title").click(function() {
    if ($(this).hasClass('truncate')) {
        $(this).removeClass('truncate');
        $(this).addClass('break-word');
    } else {
        $(this).removeClass('break-word');
        $(this).addClass('truncate');
    }
});



$(".show-note").click(function() {
    var goal_id = $(this).attr('goalid');
    // set value of text area to goal's note
    $("#note-textarea").val(
        $("#note-body-" + goal_id).text()
    );
    $("#modal-title").text(
        $("#goal-btn-" + goal_id).text()
    );
    localStorage['goal_id'] = goal_id;
    localStorage['note_changed'] = false;
    //$("#note-modal").modal("show"); // doesnt work dunno why
    $("#btn-open-modal").click(); // workaround
});

$("#note-textarea").change(function() {
    localStorage['note_changed'] = true;
});

$(".modal-wide").on("show.bs.modal", function() {
    var height = $(window).height() - 200;
    $(this).find(".modal-body").css("max-height", height);
});


$('#note-modal').on('hidden.bs.modal', function() {
    if (localStorage['note_changed'] === "true") {
        var new_note = $('#note-textarea').val();
        $('#note-body-' + localStorage['goal_id']).text(new_note);
        $.ajax('/update_note/', {
            type: "POST",
            data: {
                goal_id: localStorage['goal_id'],
                new_note: new_note
            }
        });
    }
})

// Create 

$("#create-section-btn").click(function() {
    modify_table('create_section', {
        section_title: $("#create-section-input").val()
    });
    location.reload()
});


$(".create-goal-btn").click(function() {
    var subsection_id = $(this).attr('subsectionid');
    var goal_title = $('#new-goal-input-' + subsection_id).val();
    if (goal_title === '') {
        flash_message('You must enter title of goal', 'error');
        return 0;
    }
    modify_table('create_goal', {
        goal_title: goal_title,
        subsection_id: subsection_id
    });
    location.reload();
    // todo: remove force refresh when creating new elements
});

$(".create-subs-btn").click(function() {
    var section_id = $(this).attr('sectionid');
    var subsection_title = $('#new-subs-input-' + section_id).val();
    if (subsection_title === '') {
        flash_message('You must enter subsection title', 'error');
        return 0;
    }
    modify_table('create_subsection', {
        subsection_title: subsection_title,
        section_id: section_id
    });
    location.reload();
});

$(".remove-goal-btn").click(function(event) {
    modify_table('delete_goal', {
        goal_id: $(this).attr('goalid')
    });
    location.reload();
});