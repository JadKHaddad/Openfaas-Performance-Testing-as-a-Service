document.addEventListener("DOMContentLoaded", function () {
    const deployBtn = $('#deploy-btn');
    const dismissBtn = $('#dismiss-btn');
    var code = '';
    var requirements = '';
    document.getElementById('file-input').onchange = function(evt) {
        if(!window.FileReader) return; // Browser is not compatible
        var reader = new FileReader();
        reader.onload = function(evt) {
            if(evt.target.readyState != 2) return;
            if(evt.target.error) {
                alert('Error while reading file');
                return;
            }
            code = evt.target.result;
        };
        reader.readAsText(evt.target.files[0]);
    };
    document.getElementById('requirements-input').onchange = function(evt) {
        if(!window.FileReader) return; // Browser is not compatible
        var reader = new FileReader();
        reader.onload = function(evt) {
            if(evt.target.readyState != 2) return;
            if(evt.target.error) {
                alert('Error while reading file');
                return;
            }
            requirements = evt.target.result;
        };
        reader.readAsText(evt.target.files[0]);
    };

    deployBtn.on('click', function(){
        const users = $('#users-input').val();
        const spawnRate = $('#spawn-rate-input').val();
        const host = $('#host-input').val();
        const time = $('#time-input').val();
        const fileInput = $('#file-input')[0];
        // handle false inputs
        if(users === ''){
            showInfo('Users cant be empty');
            return false
        }
        if(!isInteger(users)){
            showInfo('Users must be an integer');
            return false
        }
        if(spawnRate === ''){
            showInfo('Spawn rate cant be empty');
            return false
        }
        if(!isInteger(spawnRate)){
            showInfo('Spawn rate must be an integer');
            return false
        }
        if(fileInput.value === ''){
            showInfo('Please select a locust file');
            return false;
        }
        if(time != ''){
            if(!isInteger(time)){
                showInfo('Time must be an integer');
                return false 
            }
        }

        function callBack(data){
            if (data.success){
                const id = data.id;
                const test = CreateTest(id, users, spawnRate, host, time, 2, code, null, null, null);
                document.getElementById('tests').prepend(test);
                dismissBtn.click();
            }
        }
        if (DIRECT) {
        fetch(FUNCTIONCALL, {method: 'POST', body: JSON.stringify({command: 1, users: parseInt(users), spawn_rate: parseInt(spawnRate), host: host, time: parseInt(time), code:code, requirements:requirements})}).then(data => data.json()).then(data => 
            {
                callBack(data);
            }).catch();
        }else{
            let formData = new FormData();
            formData.append('users', users);
            formData.append('spawn_rate', spawnRate);
            formData.append('host', host);
            formData.append('time', time);
            formData.append('code', code);
            formData.append('requirements', requirements);

            fetch('/deploy', { method: 'POST', body: formData }).then(data => data.json()).then(data => {
                callBack(data);
            }).catch();
        }
        return false;
    });

    function callBack(data){
        if (data.success){
            const tests = data.tests;
            if (tests != null){
                for (var i = 0; i < tests.length; i++)(function (i) {
                    var users = null;
                    var spawn_rate = null;
                    var host = null;
                    var time =  null;
                    const info = JSON.parse(tests[i].info);
                    if (info != null){
                        users = info.users;
                        spawn_rate = info.spawn_rate;
                        host = info.host;
                        date = info.date;
                        time = info.time;
                    }
                    const test = CreateTest(tests[i].id, users, spawn_rate, host, time, tests[i].status, tests[i].code, tests[i].data, tests[i].valid, tests[i].started_at);
                    document.getElementById('tests').appendChild(test);
                })(i);
            } 
        }
    }
    if (DIRECT) {
        fetch(FUNCTIONCALL, {method:'POST', body: JSON.stringify({command: 6})}).then(data => data.json()).then(data => { // direct openfaas
            callBack(data);
        }).catch();
    }else{
        fetch('/tests').then(data => data.json()).then(data => { //server call
            callBack(data);
        }).catch();
    }
});   