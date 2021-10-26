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
                selectedProjects.push(projects[i].id);
            } else {
                // remove test from selected projects
                const index = selectedProjects.indexOf(projects[i].id);
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
    const input = document.getElementById("project-input");


    var myArray = [];
    var selectedProjects = [];

    input.onchange = function(evt) {
        const files = evt.target.files;
        myArray = []
        if(!window.FileReader) return; // Browser is not compatible
        for (var i = 0; i < evt.target.files.length ; i ++)(function (i) {
            var reader = new FileReader();
            reader.onload = function(evt) {
                if(evt.target.readyState != 2) return;
                if(evt.target.error) {
                    alert('Error while reading file');
                    return;
                }
                var file = {
                    'size' : files[i].size,
                    'type' : files[i].type,
                    'name' : files[i].webkitRelativePath,
                    'content' : evt.target.result
                } 
                //add the file obj to your array
                myArray.push(file)
            };
            reader.readAsText(files[i]);
        })(i);
        $('#add-btn').prop("disabled", false);
    };

    $('#add-btn-Modal').on('click', function(){
        $('#add-btn').prop("disabled", true);

    });
    
    $('#add-btn').on('click', function(){
        fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 1, files: myArray}) }).then(data => data.json()).then(data => {
            console.log(data);
            if (data.success){
                const task_id = data.task_id;
                var eventSource = new EventSource('/task/' + task_id);
                eventSource.onmessage = function (e) {
                    message = JSON.parse(e.data)
                    console.log(message);
                    if (!message.success){
                        console.log("Something went wrong");
                        eventSource.close();
                    }else if(message.status_code === 2){
                        console.log("installing project");
                    }else if(message.status_code === 1){
                        console.log("installing failed");
                        eventSource.close();
                        $('#spinner').addClass('hidden');
                        showInfo('Installation failed');
                    }else{
                        console.log("Task is finished");
                        eventSource.close();
                        window.location.href = '/project/' + task_id;
                    }
                };
            }
        }).catch();
        $('#dismiss-btn').click();
        $('#spinner').removeClass('hidden');
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
            // fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 7, ids: selectedprojects }) }).then(data => data.json()).then(data => {
            //     $('#dismiss-confirmation-modal-btn').click();
            //     location.reload();
            // }).catch();
        });
        return false;
    });
});