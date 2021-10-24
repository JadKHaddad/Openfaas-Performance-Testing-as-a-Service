document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("project-input");

    var contents = []

    input.onchange = function(evt) {
        if(!window.FileReader) return; // Browser is not compatible
        for (var i = 0; i < evt.target.files.length ; i ++){
            var reader = new FileReader();
            reader.onload = function(evt) {
                if(evt.target.readyState != 2) return;
                if(evt.target.error) {
                    alert('Error while reading file');
                    return;
                }
                contents.push(evt.target.result);
            };
            reader.readAsBinaryString(evt.target.files[i]);
        }
    };


    $('#add-btn').on('click', function(){
        var myArray = [];
        var file = {};
        const files = input.files;
        for(var i = 0; i < files.length; i++){
            file = {
                'size' : files[i].size,
                'type' : files[i].type,
                'name' : files[i].webkitRelativePath,
                'content' : contents[i]
            } 
            //add the file obj to your array
            myArray.push(file)
        }
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
                    }else{
                        console.log("Task is finished");
                        eventSource.close();
                    }
                };
            }
        }).catch();
        return false;
    });

    fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 3 }) }).then(data => data.json()).then(data => {
        console.log(data);
    }).catch();
});