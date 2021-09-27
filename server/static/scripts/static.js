FUNCTIONCALL = '';
DIRECT = false;

function CreateTest(id, users, spawnRate, host, time, status, code, stats, valid, startedAt) {
    var test = document.createElement('div');
    test.setAttribute('id', id);
    if (host == null) host = '';
    if (time == null) time = '';
    const template = `
    <div class="card">
        <div class="card-header">
            <div class="row">
                <div class="col-2 test-id"> ${id}</div>
                <div class="col-2"><i class="fas fa-user-alt"></i>  ${users}</div>
                <div class="col-2"><i class="fas fa-users"></i>  ${spawnRate}</div>
                <div class="col-2"><i class="fas fa-globe"></i>  ${host}</div>
                <div class="col-1"><i class="fas fa-clock"></i>  ${time}</div>
                <div class="col-1">
                    <i class="far fa-file-alt code"></i>
                </div>
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
    <img class="lin" src="">
    <img class="reg" src="">
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
    const codeLink = $(test).find('.code');
    const results = $(test).find('.card-body > .results');
    const footer = $(test).find('.card-footer');
    var intv;
    var eventSource;
    var intvSet = false;

    if (status == 0) { // not deployed
        if (valid === false) {
            notValid.removeClass('hidden');
            idCol.addClass('red');
        } else {
            check.removeClass('hidden');
        }
        stopBtn.prop("disabled", true);
        downloadBtn.prop("disabled", false);
        resultsBtn.prop("disabled", false);
    }

    if (status == 1) { // running 
        idCol.addClass('green');
        stopBtn.prop("disabled", false);
        downloadBtn.prop("disabled", true);
        elapsed.removeClass('hidden');
        spinner.removeClass('hidden');
        // get updates

        eventSource = new EventSource('/stream/' + id);
        eventSource.onmessage = function (e) {
            if (!IsJsonString(e.data)) return;
            message = JSON.parse(e.data)
            interpretMessage(message);
        };
    }

    stopBtn.on('click', function () {
        function callBack(data) {
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
        }
        if (DIRECT) {
            fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 3, id: id }) }).then(data => data.json()).then(data => {
                callBack(data);
            });
        }
        else {
            fetch('/stop/' + id, { method: 'POST' }).then(data => data.json()).then(data => {
                callBack(data);
            });
        }
    });

    downloadBtn.on('click', function () {

        var xhr = new XMLHttpRequest();
        if (DIRECT) {
            xhr.open("POST", FUNCTIONCALL);
        }
        else {
            xhr.open("POST", '/download/' + id);
        }
        xhr.responseType = "arraybuffer";
        xhr.onload = function () {
            if (this.status === 200) {
                var blob = new Blob([xhr.response], { type: "application/zip" });
                var objectUrl = URL.createObjectURL(blob);
                window.location.href = objectUrl;
            }
        };
        xhr.send(JSON.stringify({ command: 5, id: id }));
    });

    resultsBtn.on('click', function () {
        fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 2, id: id, type: "create" }) }).then(data => data.json()).then(data => {
            if (data.success) {
                if (data.status_code == 0) {
                    var xhr = new XMLHttpRequest();
                    if (DIRECT) {
                        xhr.open("POST", FUNCTIONCALL);
                    }
                    else {
                        xhr.open("POST", '/results/' + id);
                    }
                    xhr.responseType = "arraybuffer";
                    xhr.onload = function () {
                        var arrayBufferView = new Uint8Array(this.response);
                        var blob = new Blob([arrayBufferView], { type: "image/png" });
                        var urlCreator = window.URL || window.webkitURL;
                        var imageUrl = urlCreator.createObjectURL(blob);
                        $(test).find('.reg').attr({ "src": imageUrl });
                    };
                    xhr.send(JSON.stringify({ command: 2, id: id, type: "reg" }));

                    var xhr_ = new XMLHttpRequest();
                    if (DIRECT) {
                        xhr_.open("POST", FUNCTIONCALL);
                    }
                    else {
                        xhr_.open("POST", '/results/' + id);
                    }
                    xhr_.responseType = "arraybuffer";
                    xhr_.onload = function () {
                        var arrayBufferView = new Uint8Array(this.response);
                        var blob = new Blob([arrayBufferView], { type: "image/png" });
                        var urlCreator = window.URL || window.webkitURL;
                        var imageUrl = urlCreator.createObjectURL(blob);
                        $(test).find('.lin').attr({ "src": imageUrl });
                    };
                    xhr_.send(JSON.stringify({ command: 2, id: id, type: "lin" }));
                }else if (data.status_code == 2){
                    showInfo("Not enough data to analyse")
                }
            }
        });

    });

    deleteBtn.on('click', function () {
        function callBack(data) {
            if (data.success && data.deleted.includes(id)) {
                $('#dismiss-confirmation-modal-btn').click();
                $(test).remove();
                if (eventSource != null) eventSource.close();
            } else {
                showInfo('There was an error deleting the test');
            }

        }
        setConfirmationModal(id + ' Are you sure you want to delete this test?', function () {
            if (DIRECT) {
                fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 7, ids: [id] }) }).then(data => data.json()).then(data => {
                    callBack(data);
                }).catch();
            } else {
                let formData = new FormData();
                formData.append('ids', '["' + id + '"]');
                fetch('/delete', { method: 'POST', body: formData }).then(data => {
                    callBack(data);
                }).catch();
            }
        });
        return false;
    });

    if (stats != null) {
        const jData = JSON.parse(stats)
        update(jData);
    }

    codeLink.on('click', function () {
        setUpCode(code);
    });

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
                showInfo(id + 'There was an error running your locust file');
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

function showInfo(message) {
    // set message
    $('#info-message').text(message);
    // show message
    $('#info-modal-button').click();
}

function setUpCode(code) {
    // set code
    $('#code').text(code);
    // show code
    $('#code-modal-button').click();
}

function setConfirmationModal(message, func) {
    // set message
    $('#confirm-message').text(message);
    // unbind
    $('#confirm-delete').off('click');
    // bind
    $('#confirm-delete').on('click', function () {
        func();
    });
    // show
    $('#confirmation-modal-button').click();
}

function isInteger(str) {
    var pattern = /^\d+$/;
    return pattern.test(str);
}

function IsJsonString(str) {
    try {
        JSON.parse(str);
    } catch (e) {
        return false;
    }
    return true;
}

document.addEventListener("DOMContentLoaded", function () {
    FUNCTIONCALL = document.getElementById('function-call').innerText;
    DIRECT = (document.getElementById('direct').innerText === 'true');
});