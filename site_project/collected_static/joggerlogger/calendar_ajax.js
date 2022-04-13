var calendar;
var calendarEl

document.addEventListener('DOMContentLoaded', function() {
    calendarEl = document.getElementById('calendar');
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        themeSystem: 'bootstrap',
        buttonIcons: {
            prev: 'fa-chevron-left',
            next: 'fa-chevron-right'
        },
        dateClick: on_click,
        eventColor: "#a0a0a0",
        eventBackgroundColor: "rgb(52, 58, 64)",
        eventClassNames: ['m-0', 'p-0', 'event-custom'],
        eventClick: function(info) {
            $("#displayModal").modal('show');
            $("#displayModal_title").text(info.event.extendedProps['title']);
            $("#displayModal_date").text(info.event.startStr);
            $("#displayModal_distdur").text(info.event.title);
            $("#displayModal_description").text(info.event.extendedProps['description']);
            $("#displayModal_delete").removeAttr('onclick');
            $("#displayModal_delete").attr('onclick', 'delete_run(' + info.event.id + ')');

            $("#displayModal_edit").removeAttr('onclick');
            $("#displayModal_edit").attr('onclick', 'edit_run(' + info.event.id + ')');
        }
    });
    calendar.render();
});

function get_csrf_token() {
    let token = document.getElementsByName('csrfmiddlewaretoken')[0].value
    return token
}

function edit_run(id) {
    let event = calendar.getEventById(id)

    $("#displayModal").modal('hide');
    $("#formModal").modal('show');

    $("#formModal_id"   ).val(id);
    $("#formModal_title").val(event.extendedProps['title']);
    $("#formModal_dist" ).val(event.extendedProps['distance']);
    $("#formModal_dur"  ).val(event.extendedProps['duration']);
    $("#formModal_desc" ).val(event.extendedProps['description']);
    $("#run-form-date"  ).val(event.startStr);
}

function delete_run(id) {
    $("#displayModal").modal('hide');
    let request = new XMLHttpRequest(
        {headers: {'X-CSRFToken': get_csrf_token()}}
    )
    request.onreadystatechange = function() {
        if (request.readyState != 4) return
        update_page()
    }
    request.open("DELETE", "/api/runs?id=" + id)
    request.setRequestHeader('X-CSRFToken', get_csrf_token())
    request.send()
}

function update_page() {
    let request = new XMLHttpRequest()
    request.onreadystatechange = function() {
        if (request.readyState != 4) return
        parse_response(request)
    }
    
    request.open("GET", "/api/runs?user=" + username)
    request.send()
}

function parse_response(response) {
    let json = JSON.parse(response.responseText)

    calendar.removeAllEvents()
    for(let i = 0; i < json.length; i++) {
        let id = json[i]['id']
        calendar.addEvent(json[i])
        let event = calendar.getEventById(id)
    }
}