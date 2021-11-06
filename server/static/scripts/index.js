var selectedProjects = [];

function createProjectsList(projects) {
    var list = document.createElement('div');
    list.classList.add('list-group');
    for (var i = 0; i < projects.length; i++)  (function (i) {
        var item = document.createElement('a');
        item.setAttribute('id', projects[i]);
        item.classList.add('list-group-item');
        item.classList.add('list-group-item-action');
        const template = `
            <div class="form-check">
            <input
                class="form-check-input"
                type="checkbox"
                value=""
                id="flexCheckDefault-${projects[i]}"
            />
            <label class="test-label">
                ${projects[i]}
            </label>
            </div>
        `;
        item.innerHTML = template;
        // handle check box events
        $(item).find('input').change(function () {

            if (this.checked) {
                $('#delete-project').prop("disabled", false);
                // add test to selected projects
                selectedProjects.push(projects[i]);
            } else {
                // remove test from selected projects
                const index = selectedProjects.indexOf(projects[i]);
                if (index > -1) {
                    selectedProjects = selectedProjects.splice(index + 1, 1);
                }
                if (selectedProjects.length < 1) {
                    $('#delete-project').prop("disabled", true);
                }
            }
        });

        $(item).find('label').on('click', function () {
            window.location.href = '/project/' + projects[i];
        });
        list.appendChild(item);
    })(i);
    return list;
}

document.addEventListener("DOMContentLoaded", function () {
    $('#add-btn').on('click', function(){
        const input = document.getElementById("project-input");
        const files = input.files;
        if (files.length < 1){
            showInfo('Please select a directory to upload');
            return false;
        }
        var data = new FormData()
        for(var i = 0; i < files.length ; i++){
            data.append('file' + i, files[i])
        }
        $('#dismiss-btn').click();
        $('#spinner').removeClass('hidden');

        fetch(FUNCTIONCALL, {method: 'POST', body: data}).then(data => data.json()).then(data => {
            console.log(data);
            if (data.success){
                const task_id = data.task_id;
                var eventSource;
                var socketIntv;
                function onMessage(message){
                    if (!message.success){
                        console.log("Something went wrong");
                        $('#spinner').addClass('hidden');
                        showInfo('Something went wrong');
                        if(WEBSOCKET){
                            clearInterval(socketIntv);
                        }else{
                            eventSource.close();
                        }
                    }else if(message.status_code === 3){
                            console.log("thread is locking");
                    }else if(message.status_code === 2){
                        console.log("installing project");
                    }else if(message.status_code === 1){
                        console.log("installing failed");
                        if(WEBSOCKET){
                            clearInterval(socketIntv);
                        }else{
                            eventSource.close();
                        }
                        $('#spinner').addClass('hidden');
                        showInfo('Installation failed');
                    }else{
                        console.log("Task is finished");
                        if(WEBSOCKET){
                            clearInterval(socketIntv);
                        }else{
                            eventSource.close();
                        }
                        window.location.href = '/project/' + task_id;
                    }
                };

                if (WEBSOCKET){
                    socketIntv = setInterval(function () {
                        socket.emit('task_stats', { project_name: task_id});
                    }, 1000);
                    socket.on(task_id, function (msg) {
                        if (!IsJsonString(msg.data)) return;
                        var message = JSON.parse(msg.data);
                        onMessage(message);
                    });
                }else{
                    eventSource = new EventSource('/task/' + task_id);
                    eventSource.onmessage = function (e) {
                        var message = JSON.parse(e.data);
                        console.log(message);
                        onMessage(message);
                    };
                }



            }else{
                $('#spinner').addClass('hidden');
                showInfo(data.message);
            }
        }).catch( e => {
            $('#spinner').addClass('hidden');
            showInfo('Something went wrong');
        });
        return false;
    });

    fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 3 }) }).then(data => data.json()).then(data => {
        if (data.success) {
            const projects = data.projects;
            $('#content').append(createProjectsList(projects));
        }
    }).catch();

    const deleteBtn = $('#delete-project');
    deleteBtn.prop("disabled", true);
    //handle delete button
    deleteBtn.on("click", function () {
        setConfirmationModal('Are you sure you want to delete these projects?', function () {
            fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 10, names: selectedProjects }) }).then(data => data.json()).then(data => {
                location.reload();
            }).catch();
            $('#dismiss-confirmation-modal-btn').click();
        });
        return false;
    });
});