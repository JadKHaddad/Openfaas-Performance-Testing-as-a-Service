document.addEventListener("DOMContentLoaded", function () {
    $('#kill-btn').on('click', function () {
        setConfirmationModal('Kill all running tasks? Istallation tasks will also be killed', function () {
            fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 911 }) }).then(data => data.json()).then(data => {
                if (data.success) {
                    $('#dismiss-confirmation-modal-btn').click();
                    showInfo('Success', 'green');
                } else {
                    showInfo('There was an error killing running tasks','red');
                }
            }).catch(function(){
                showInfo('Could not connect to server','red');
            });
        }, 'Kill');
        return false;
    });

    $('#cleanup-btn').on('click', function () {
        setConfirmationModal('Delete all projects?', function () {
            fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 912 }) }).then(data => data.json()).then(data => {
                if (data.success) {
                    $('#dismiss-confirmation-modal-btn').click();
                    showInfo('Success', 'green');
                } else {
                    showInfo('There was an error deleting projects','red');
                }
            }).catch(function(){
                showInfo('Could not connect to server','red');
            });
        }, 'Delete');
        return false;
    });

    // get all runnig tests
    fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 13 }) }).then(data => data.json()).then(data => {
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
                    const project_name = tests[i].project_name;
                    const script_name = tests[i].script_name;
                    const info = JSON.parse(tests[i].info.info);
                    if (info != null) {
                        users = info.users;
                        spawn_rate = info.spawn_rate;
                        host = info.host;
                        time = info.time;
                        workers = info.workers;
                        started_at = info.started_at;
                    }
                    const test = CreateTest(project_name, script_name, tests[i].info.id, users, spawn_rate, workers, host, time, tests[i].info.status, tests[i].info.data, tests[i].info.valid, started_at, true);

                    document.getElementById('tests').appendChild(test);
                })(i);
            }
        }
    }).catch(function(){
        showInfo('Could not connect to server','red');
    });
});

