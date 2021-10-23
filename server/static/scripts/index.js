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

        const projectName = $('#name-input').val();
        fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 1, name: projectName, files: myArray}) }).then(data => data.json()).then(data => {
            console.log(data.message);
            if (data.success){
                console.log("success");
            }
        }).catch();
        return false;
    });
});