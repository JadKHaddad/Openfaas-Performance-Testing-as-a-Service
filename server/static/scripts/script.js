document.addEventListener("DOMContentLoaded", function () {
    const project_name = document.getElementById('project-name').innerText;
    const script_name = document.getElementById('script-name').innerText;
    const startBtn = $('#start-btn');
    const deleteBtn = $('#delete-script-tests');
    const dismissBtn = $('#dismiss-btn');

    startBtn.on('click', function () {
        const users = $('#users-input').val();
        const spawnRate = $('#spawn-rate-input').val();
        const workers = $('#workers-input').val();
        var host = $('#host-input').val().replace("http://", "").replace("https://", "");
        if (host != ""){
            host = "http://" + host;
        }
        const time = $('#time-input').val();
        // handle false inputs
        if (users === '') {
            showInfo('Users cant be empty','red');
            return false
        }
        if (!isInteger(users)) {
            showInfo('Users must be an integer','red');
            return false
        }
        if (spawnRate === '') {
            showInfo('Spawn rate cant be empty','red');
            return false
        }
        if (!isInteger(spawnRate)) {
            showInfo('Spawn rate must be an integer','red');
            return false
        }
        if (workers !== '' && !isInteger(workers)) {
            showInfo('workers must be an integer','red');
            return false
        }

        if (time != '') {
            if (!isInteger(time)) {
                showInfo('Time must be an integer','red');
                return false;
            }
        }

        startTest(project_name, script_name, users, spawnRate, workers, host, time, dismissBtn, false);
        if (host != ""){
            localStorage.setItem('last_host', host);
        }
        return false;
    });

    deleteBtn.on('click', function () {
        setConfirmationModal(script_name + ': Are you sure you want to delete all tests?', function () {
            fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 16, project_name: project_name, script_name: script_name}) }).then(data => data.json()).then(data => {
                if (data.success) {
                    location.reload(true);
                } else {
                    showInfo('There was an error deleting tests', 'red');
                }
            }).catch(function(){
                showInfo('Could not connect to server', 'red');
            });
        });
        return false;
    });

    $('#host-input').val(localStorage.getItem('last_host'));
    // get tests of this script
    fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 7, project_name: project_name, script_name: script_name }) }).then(data => data.json()).then(data => {
        if (data.success) {
            const tests = data.tests;
            console.log(tests);
            if (tests != null) {
                for (var i = 0; i < tests.length; i++)(function (i) {
                    var users = null;
                    var spawn_rate = null;
                    var host = null;
                    var time = null;
                    var workers = null;
                    var started_at = null;
                    const info = JSON.parse(tests[i].info);
                    if (info != null) {
                        users = info.users;
                        spawn_rate = info.spawn_rate;
                        host = info.host;
                        time = info.time;
                        workers = info.workers;
                        started_at = info.started_at;
                    }
                    const test = CreateTest(project_name, script_name, tests[i].id, users, spawn_rate, workers, host, time, tests[i].status, tests[i].data, tests[i].valid, started_at, false);

                    document.getElementById('tests').appendChild(test);
                })(i);
            }
        }
    }).catch(function(){
        showInfo('Could not connect to server','red');
    });
});