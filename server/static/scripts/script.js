function CreateTest(project_name, script_name, id, users, spawnRate, workers, host, time, status, stats, valid, startedAt) {
    var test = document.createElement('div');
    test.setAttribute('id', id);
    if (host == null) host = '';
    if (time == null) time = '';
    const template = `
    <div class="test-container">
        <div class="buttons btn-container">
        <button type="button" class="btn btn-primary stop-test" disabled>
            Stop
        </button>
        <button type="button" class="btn btn-primary download-test" disabled>
            Download
        </button>
        <button type="button" class="btn btn-primary show-test-results" disabled>
        Show results
        </button>
        <button type="button" class="btn btn-danger delete-test">Delete</button>
        </div>
        <div class="img-container">
        <img class="lin hidden" src="">
        <img class="reg hidden" src="">
        </div>
        <div class="card">
            <div class="card-header">
                <div class="row">
                    <div class="col-3 test-id"> ${id}</div>
                    <div class="col-1"><i class="fas fa-user-alt"></i>  ${users}</div>
                    <div class="col-1"><i class="fas fa-users"></i>  ${spawnRate}</div>
                    <div class="col-1"><i class="fas fa-hard-hat"></i> ${workers}</div>
                    <div class="col-3"><i class="fas fa-globe"></i>  ${host}</div>
                    <div class="col-1"><i class="fas fa-clock"></i>  ${time}</div>
                    <div class="col-1 elapsed hidden"><i class="fas fa-stopwatch"></i>  <label class="elapsed-text"></label></div>
                    <div class="col-1">
                        <div class="spinner-border text-primary spinner hidden"></div>
                        <i class="fas fa-check check hidden"></i>
                        <i class="fas fa-times not-valid hidden"></i>
                    </div>

                </div>
            </div>
            <div class="card-body">
                <div class="container-fluid">
                    <div class="row">
                        <div class="col-1">Type</div>
                        <div class="col-2">Name</div>
                        <div class="col-1">Requests</div>
                        <div class="col-1">Fails</div>
                        <div class="col-1">Med</div>
                        <div class="col-1">Avg (ms)</div>
                        <div class="col-1">Min (ms)</div>
                        <div class="col-1">Max (ms)</div>
                        <div class="col-1">Avg size (bytes)</div>
                        <div class="col-1">RPS</div>
                        <div class="col-1">FPS</div>
                    </div>
                </div>
                <div class="container-fluid results">
                </div>
            </div>
            <div class="card-footer">

            </div>
        </div>
    </div>
    `;

    test.innerHTML = template;
    const idCol = $(test).find('.test-id');
    const stopBtn = $(test).find('.stop-test');
    const downloadBtn = $(test).find('.download-test');
    const resultsBtn = $(test).find('.show-test-results');
    const deleteBtn = $(test).find('.delete-test');
    const spinner = $(test).find('.spinner');
    const check = $(test).find('.check');
    const notValid = $(test).find('.not-valid');
    const elapsed = $(test).find('.elapsed');
    const elapsedText = $(test).find('.elapsed-text');
    const results = $(test).find('.card-body > .results');
    const footer = $(test).find('.card-footer');
    const lin = $(test).find('.lin');
    const reg = $(test).find('.reg');
    var intv;
    var eventSource;
    var intvSet = false;

    if (status == 0) { // not running
        stopBtn.prop("disabled", true);
        downloadBtn.prop("disabled", false);
        resultsBtn.prop("disabled", false);
        if (valid === false) {
            notValid.removeClass('hidden');
            idCol.addClass('red');
            downloadBtn.prop("disabled", true);
            resultsBtn.prop("disabled", true);
        } else {
            check.removeClass('hidden');
        }

    }

    if (status == 1) { // running 
        idCol.addClass('green');
        stopBtn.prop("disabled", false);
        downloadBtn.prop("disabled", true);
        elapsed.removeClass('hidden');
        spinner.removeClass('hidden');
        // get updates

        eventSource = new EventSource('/stream/' + project_name + "/" + script_name + "/" + id);
        eventSource.onmessage = function (e) {
            if (!IsJsonString(e.data)) return;
            message = JSON.parse(e.data)
            interpretMessage(message);
        };
    }

    stopBtn.on('click', function () {
        fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 8, project_name: project_name, script_name: script_name, id: id }) }).then(data => data.json()).then(data => {
            if (data.success) {
                idCol.removeClass('green').removeClass('red');
                clearInterval(intv);
                check.removeClass('hidden');
                spinner.addClass('hidden');
                stopBtn.prop("disabled", true);
                downloadBtn.prop("disabled", false);
                resultsBtn.prop("disabled", false);
                eventSource.close();
            } else {
                showInfo('There was an error stopping the test');
            }
        });
    });

    downloadBtn.on('click', function () {
        fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 5, id: id }) }).then(response => response.blob()).then(blob => {
            var objectUrl = URL.createObjectURL(blob);
            window.location.href = objectUrl;
        });

    });

    resultsBtn.on('click', function () {
        if (lin.hasClass('hidden') && reg.hasClass('hidden')) {
            if (lin.attr('src') == '' && reg.attr('src') == '') {
                fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 2, id: id, type: 1 }) }).then(data => data.json()).then(data => {
                    if (data.success) {
                        if (data.status_code == 0) {
                            fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 2, id: id, type: 2 }) }).then(response => response.blob()).then(blob => {
                                var urlCreator = window.URL || window.webkitURL;
                                const imageUrl = urlCreator.createObjectURL(blob);
                                lin.attr({ "src": imageUrl });
                                fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 2, id: id, type: 3 }) }).then(response => response.blob()).then(blob => {
                                    var urlCreator = window.URL || window.webkitURL;
                                    const imageUrl = urlCreator.createObjectURL(blob);
                                    reg.attr({ "src": imageUrl });
                                    resultsBtn.text('Hide results');
                                });
                            });
                        } else if (data.status_code == 2) {
                            showInfo("Not enough data to analyse");
                            resultsBtn.prop("disabled", true);
                        }
                    }
                });
            }
            lin.removeClass('hidden');
            reg.removeClass('hidden');
        } else {
            lin.addClass('hidden');
            reg.addClass('hidden');
            resultsBtn.text('Show results');
        }
    });

    deleteBtn.on('click', function () {
        setConfirmationModal(id + ' Are you sure you want to delete this test?', function () {
            fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 9, project_name: project_name, script_name: script_name, id: id }) }).then(data => data.json()).then(data => {
                if (data.success) {
                    $('#dismiss-confirmation-modal-btn').click();
                    $(test).remove();
                    if (eventSource != null) eventSource.close();
                } else {
                    showInfo('There was an error deleting the test');
                }
            }).catch();
        });
        return false;
    });

    if (stats != null) {
        const jData = JSON.parse(stats)
        update(jData);
    }

    function interpretMessage(message) {
        if (message.success) {
            if (message.status == 0) {
                // test is not running
                clearInterval(intv);
                idCol.removeClass('green').removeClass('red');
                check.removeClass('hidden');
                spinner.addClass('hidden');
                stopBtn.prop("disabled", true);
                downloadBtn.prop("disabled", false);
                resultsBtn.prop("disabled", false);
                eventSource.close();
                return;
            }
            if (!intvSet) {
                intv = setInterval(function () {
                    elapsedText.text(parseInt((Date.now() / 1000) - startedAt));
                }, 1000);
                intvSet = true;
            }
            const jData = JSON.parse(message.data)
            update(jData);
        } else {
            if (message.exit_code == 4) {
                showInfo(id + ' There was an error running your locust file');
                clearInterval(intv);
                idCol.removeClass('green').addClass('red');
                notValid.removeClass('hidden');
                elapsed.addClass('hidden');
                spinner.addClass('hidden');
                stopBtn.prop("disabled", true);
                downloadBtn.prop("disabled", true);
                eventSource.close();
                return;
            }
        }
    }
    // update results
    function update(jData) {
        footer.children().remove();
        results.children().remove();
        for (var i = 0; i < jData.length; i++) {
            var type = jData[i]["Type"];
            const name = jData[i]["Name"];
            const requests = jData[i]["Request Count"];
            const fails = jData[i]["Failure Count"];
            const med = jData[i]["Median Response Time"];
            const avg = jData[i]["Average Response Time"].toString().slice(0, 8);
            const min = jData[i]["Min Response Time"].toString().slice(0, 8);
            const max = jData[i]["Max Response Time"].toString().slice(0, 8);
            const avgSize = jData[i]["Average Content Size"].toString().slice(0, 8);
            const rps = jData[i]["Requests/s"].toString().slice(0, 8);
            const fps = jData[i]["Failures/s"].toString().slice(0, 8);
            if (i == jData.length - 1) {
                type = '';
                footer.append(createRow(type, name, requests, fails, med, avg, min, max, avgSize, rps, fps));
            } else {
                results.append(createRow(type, name, requests, fails, med, avg, min, max, avgSize, rps, fps));
            }
        }
    }
    return test;
}

function createRow(type, name, requests, fails, med, avg, min, max, avgSize, rps, fps) {
    var row = document.createElement('div');
    row.classList.add('row');
    const template = `
        <div class="col-1">${type}</div>
        <div class="col-2">${name}</div>
        <div class="col-1">${requests}</div>
        <div class="col-1">${fails}</div>
        <div class="col-1">${med}</div>
        <div class="col-1">${avg}</div>
        <div class="col-1">${min}</div>
        <div class="col-1">${max}</div>
        <div class="col-1">${avgSize}</div>
        <div class="col-1">${rps}</div>
        <div class="col-1">${fps}</div>
    `;
    row.innerHTML = template;
    return row;
}

document.addEventListener("DOMContentLoaded", function () {
    const project_name = document.getElementById('project-name').innerText;
    const script_name = document.getElementById('script-name').innerText;
    const startBtn = $('#start-btn');
    const dismissBtn = $('#dismiss-btn');

    startBtn.on('click', function () {
        const users = $('#users-input').val();
        const spawnRate = $('#spawn-rate-input').val();
        const workers = $('#workers-input').val();
        const host = $('#host-input').val();
        const time = $('#time-input').val();
        // handle false inputs
        if (users === '') {
            showInfo('Users cant be empty');
            return false
        }
        if (!isInteger(users)) {
            showInfo('Users must be an integer');
            return false
        }
        if (spawnRate === '') {
            showInfo('Spawn rate cant be empty');
            return false
        }
        if (!isInteger(spawnRate)) {
            showInfo('Spawn rate must be an integer');
            return false
        }
        if (workers !== '' && !isInteger(workers)) {
            showInfo('workers must be an integer');
            return false
        }

        if (time != '') {
            if (!isInteger(time)) {
                showInfo('Time must be an integer');
                return false;
            }
        }

        fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 5, project_name: project_name, script_name: script_name, users: parseInt(users), spawn_rate: parseInt(spawnRate), workers: parseInt(workers), host: host, time: parseInt(time) }) }).then(data => data.json()).then(data => {
            if (data.success) {
                const id = data.id;
                const started_at = data.started_at;
                const test = CreateTest(project_name, script_name, id, users, spawnRate, workers, host, time, 1, null, null, started_at);
                document.getElementById('tests').prepend(test);
                dismissBtn.click();
            }
        }).catch();
        return false;
    });

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
                    const test = CreateTest(project_name, script_name, tests[i].id, users, spawn_rate, workers, host, time, tests[i].status, tests[i].data, tests[i].valid, started_at);

                    document.getElementById('tests').appendChild(test);
                })(i);
            }
        }
    }).catch();
});