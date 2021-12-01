FUNCTIONCALL = '/proxy'
WEBSOCKET = false;
var socket;

function CreateTest(project_name, script_name, id, users, spawnRate, workers, host, time, status, stats, valid, startedAt, showPath) {
    var test = document.createElement('div');
    test.setAttribute('id', id);
    if (host == null) host = '';
    if (time == null) time = '';
    if (workers == 0) workers = '';
    path = '';
    if (showPath){
        path =`
        <div class="path">
            <a href="/project/${project_name}">${project_name}</a>&nbsp;&nbsp;<i class="fas fa-angle-right"></i>&nbsp;&nbsp;<a href="/project/${project_name}/${script_name}">${script_name}</a>
        </div>
        `;
    }
    const template = `
    <div class="test-container">
        <div class="buttons btn-container">
            <button type="button" class="btn btn-primary stop-test" disabled>
                Stop
            </button>
            <button type="button" class="btn btn-primary restart-test" disabled>
                Restart
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
        ${path}
        <div class="card">
            <div class="card-header">
                <div class="row">
                    <div class="col-3 test-id" data-mdb-toggle="tooltip" title="Test id"> ${id}</div>
                    <div class="col-1" data-mdb-toggle="tooltip" title="Users"><i class="fas fa-user-alt"></i>  ${users}</div>
                    <div class="col-1" data-mdb-toggle="tooltip" title="Spawn rate"><i class="fas fa-users"></i>  ${spawnRate}</div>
                    <div class="col-1" data-mdb-toggle="tooltip" title="Workers"><i class="fas fa-hard-hat"></i> ${workers}</div>
                    <div class="col-3" data-mdb-toggle="tooltip" title="Host"><i class="fas fa-globe"></i>  ${host}</div>
                    <div class="col-1" data-mdb-toggle="tooltip" title="Time is seconds"><i class="fas fa-clock"></i>  ${time}</div>
                    <div class="col-1 elapsed hidden" data-mdb-toggle="tooltip" title="Elapsed time is seconds"><i class="fas fa-stopwatch" ></i>  <label class="elapsed-text"></label></div>
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
    const card = $(test).find('.card');
    const idCol = $(test).find('.test-id');
    const stopBtn = $(test).find('.stop-test');
    const restartBtn = $(test).find('.restart-test');
    const downloadBtn = $(test).find('.download-test');
    const resultsBtn = $(test).find('.show-test-results');
    const deleteBtn = $(test).find('.delete-test');
    const spinner = $(test).find('.spinner');
    const check = $(test).find('.check');
    const notValid = $(test).find('.not-valid');
    const elapsed = $(test).find('.elapsed');
    const elapsedText = $(test).find('.elapsed-text');
    const body = $(test).find('.card-body');
    const results = body.find('.results');
    const footer = $(test).find('.card-footer');
    const lin = $(test).find('.lin');
    const reg = $(test).find('.reg');
    var intv;
    var eventSource;
    var intvSet = false;
    var socketIntv;

    if (status == 0) { // not running
        stopBtn.prop("disabled", true);
        downloadBtn.prop("disabled", false);
        restartBtn.prop("disabled", false);
        resultsBtn.prop("disabled", false);
        if (valid === false) {
            notValid.removeClass('hidden');
            idCol.addClass('red');
            downloadBtn.prop("disabled", true);
            restartBtn.prop("disabled", true);
            resultsBtn.prop("disabled", true);
        } else {
            check.removeClass('hidden');
        }

    }

    if (status == 1) { // running 
        idCol.addClass('green');
        stopBtn.prop("disabled", false);
        downloadBtn.prop("disabled", true);
        restartBtn.prop("disabled", true);
        elapsed.removeClass('hidden');
        spinner.removeClass('hidden');
        // get updates
        if (WEBSOCKET){
            socketIntv = setInterval(function () {
                socket.emit('stats', { project_name: project_name, script_name: script_name, id:id });
            }, 1000);
            socket.on(id, function (msg) {
                if (!IsJsonString(msg.data)) return;
                message = JSON.parse(msg.data)
                interpretMessage(message);
            });
        }else{
            eventSource = new EventSource('/stream/' + project_name + "/" + script_name + "/" + id);
            eventSource.onmessage = function (e) {
                if (!IsJsonString(e.data)) return;
                message = JSON.parse(e.data)
                interpretMessage(message);
            };
        }

    }

    card.on('dblclick', function(){
        body.slideToggle();
    });

    stopBtn.on('click', function () {
        fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 8, project_name: project_name, script_name: script_name, id: id }) }).then(data => data.json()).then(data => {
            if (data.success) {
                idCol.removeClass('green').removeClass('red');
                clearInterval(intv);
                check.removeClass('hidden');
                spinner.addClass('hidden');
                stopBtn.prop("disabled", true);
                downloadBtn.prop("disabled", false);
                restartBtn.prop("disabled", false);
                resultsBtn.prop("disabled", false);
                if(WEBSOCKET){
                    clearInterval(socketIntv);
                }else{
                    eventSource.close();
                }
                
            } else {
                showInfo('There was an error stopping the test', 'red');
            }
        });
    });

    restartBtn.on('click', function(){
        startTest(project_name, script_name, users, spawnRate, workers, host, time, $('#dismiss-btn'), window.location.pathname == '/control');
    });

    downloadBtn.on('click', function () {
        fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 11, project_name: project_name, script_name: script_name, id: id }) }).then(response => response.blob()).then(blob => {
            var objectUrl = URL.createObjectURL(blob);
            window.location.href = objectUrl;
        });

    });

    resultsBtn.on('click', function () {
        if (lin.hasClass('hidden') && reg.hasClass('hidden')) {
            if (lin.attr('src') == '' && reg.attr('src') == '') {
                fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 12, project_name: project_name, script_name: script_name, id: id , type: 1 }) }).then(data => data.json()).then(data => {
                    if (data.success) {
                        if (data.status_code == 0) {
                            fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 12, project_name: project_name, script_name: script_name, id: id, type: 2 }) }).then(response => response.blob()).then(blob => {
                                var urlCreator = window.URL || window.webkitURL;
                                const imageUrl = urlCreator.createObjectURL(blob);
                                lin.attr({ "src": imageUrl });
                                fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 12, project_name: project_name, script_name: script_name, id: id, type: 3 }) }).then(response => response.blob()).then(blob => {
                                    var urlCreator = window.URL || window.webkitURL;
                                    const imageUrl = urlCreator.createObjectURL(blob);
                                    reg.attr({ "src": imageUrl });
                                    resultsBtn.text('Hide results');
                                });
                            });
                        } else if (data.status_code == 2) {
                            showInfo("Not enough data to analyse", "red");
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
                    if(WEBSOCKET){
                        if (socketIntv != null) clearInterval(socketIntv);
                    }else{
                        if (eventSource != null) eventSource.close();
                    }
                    
                } else {
                    showInfo('There was an error deleting the test', 'red');
                }
            }).catch(function(){
                showInfo('Could not connect to server', 'red');
            });
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
                restartBtn.prop("disabled", false);
                resultsBtn.prop("disabled", false);
                if(WEBSOCKET){
                    clearInterval(socketIntv);
                }else{
                    eventSource.close();
                }
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
                showInfo(id + ' There was an error running your locust file', 'red');
                clearInterval(intv);
                idCol.removeClass('green').addClass('red');
                notValid.removeClass('hidden');
                elapsed.addClass('hidden');
                spinner.addClass('hidden');
                stopBtn.prop("disabled", true);
                downloadBtn.prop("disabled", true);
                restartBtn.prop("disabled", true);
                if(WEBSOCKET){
                    clearInterval(socketIntv);
                }else{
                    eventSource.close();
                }
                return;
            }
        }
    }
    // update results
    function update(jData) {
        if(jData != null){
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

function startTest(project_name, script_name, users, spawnRate, workers, host, time, dismissBtn, showPath){
    fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 5, project_name: project_name, script_name: script_name, users: parseInt(users), spawn_rate: parseInt(spawnRate), workers: parseInt(workers), host: host, time: parseInt(time) }) }).then(data => data.json()).then(data => {
        if (data.success) {
            const id = data.id;
            const started_at = data.started_at;
            const test = CreateTest(project_name, script_name, id, users, spawnRate, workers, host, time, 1, null, null, started_at, showPath);
            document.getElementById('tests').prepend(test);
            if (dismissBtn != null){
                dismissBtn.click();
            }
        }
    }).catch(function(){
        showInfo('Could not connect to server','red');
    });
}

function showInfo(message, color, error) {


    $('#info-message').removeClass('red');
    $('#info-message').removeClass('green');
    $('#info-message').addClass(color);

    if (error != null && error != 'None'){
        $('#info-error').removeClass('hidden');
        $('#info-error').html(error);
    }else{
        $('#info-error').addClass('hidden');
    }
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

function setConfirmationModal(message, func, buttonText) {
    // set message
    $('#confirm-message').text(message);
    // unbind
    $('#confirm-delete').off('click');
    // bind
    $('#confirm-delete').on('click', function () {
        func();
    });
    if (buttonText != null){
        $('#confirm-delete').html(buttonText);
    }
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

function getHostName(urlStr){
    var l = new URL(urlStr)
    return l.hostname + ':' + l.port;
}

function setCookie(name, value, daysToLive) {
    // Encode value in order to escape semicolons, commas, and whitespace
    var cookie = name + "=" + encodeURIComponent(value);
    
    if(typeof daysToLive === "number") {
        /* Sets the max-age attribute so that the cookie expires
        after the specified number of days */
        cookie += "; max-age=" + (daysToLive*24*60*60) + ";path=/";
        
        document.cookie = cookie;
    }
}

function getCookie(name) {
    // Split cookie string and get all individual name=value pairs in an array
    var cookieArr = document.cookie.split(";");
    
    // Loop through the array elements
    for(var i = 0; i < cookieArr.length; i++) {
        var cookiePair = cookieArr[i].split("=");
        
        /* Removing whitespace at the beginning of the cookie name
        and compare it with the given string */
        if(name == cookiePair[0].trim()) {
            // Decode the cookie value and return
            return decodeURIComponent(cookiePair[1]);
        }
    }
    // Return null if not found
    return null;
}

// rotate element
$.fn.animateRotate = function(angle, duration, easing, complete) {
    var args = $.speed(duration, easing, complete);
    var step = args.step;
    return this.each(function(i, e) {
      args.complete = $.proxy(args.complete, e);
      args.step = function(now) {
        $.style(e, 'transform', 'rotate(' + now + 'deg)');
        if (step) return step.apply(e, arguments);
      };
  
      $({deg: 0}).animate({deg: angle}, args);
    });
  };

document.addEventListener("DOMContentLoaded", function () {
    const functionName = document.getElementById('function-name').innerText;
    var openfaasUrl = document.getElementById('openfaas-url').innerText;
    var direct = false;
    if (document.getElementById('direct').innerText === 'true') direct = true;
    if (document.getElementById('websocket').innerText === 'true') WEBSOCKET  = true;

    if (getCookie('openfaasurl') != null){
        openfaasUrl = getCookie('openfaasurl');
    }

    if (getCookie('direct') != null){
        direct = false;
        if(getCookie('direct') === 'true') direct = true;
    }

    if (getCookie('theme') != null){
        if(getCookie('theme') === 'dark') {
            $('#dark-theme-checkbox').prop('checked', true);
        };
    }

    if (getCookie('noredges') != null){
        if(getCookie('noredges') === 'true') {
            $('#i-do-not-like-rounded-edges-checkbox').prop('checked', true);
        };
    }

    $('#url-input').val(openfaasUrl);
    $('#url').text(openfaasUrl);
    $('#nav-url').on('click', function(){
        $('#gear').animateRotate(180);
        $('#url-modal-button').click();
        $('*').bind('click.myEvents', function(event){
            if(event.currentTarget == $('#Url-Modal')[0]){
                $('#gear').animateRotate(-180);
                $('*').off('.myEvents');
            }
            event.stopPropagation();
            
        });
        return false;
    });

    $('#set-url-btn').on('click',function(){
        var newOpenfaasUrl = FUNCTIONCALL;
        openfaasUrl = $('#url-input').val();
        openfaasUrl = openfaasUrl.replace("http://", "").replace("https://", "");
        openfaasUrl = "http://" + openfaasUrl;
        direct = false;
        noredges = false;
        theme = 'light'
        if($('#direct-checkbox').prop('checked') == true) direct = true; 
        if($('#no-openfaas-checkbox').prop('checked') == true) openfaasUrl = 'None';
        if($('#i-do-not-like-rounded-edges-checkbox').prop('checked') == true) noredges = true;
        if($('#dark-theme-checkbox').prop('checked') == true) theme = 'dark'; 

        if (openfaasUrl === 'None'){
            newOpenfaasUrl = '/local';
        }else if (direct){
            if (openfaasUrl.slice(-1) == '/'){
                openfaasUrl = openfaasUrl.slice(0, -1);
            }
            newOpenfaasUrl = `${openfaasUrl}/function/${functionName}`;
        }

        function onSuccess(){
            setCookie('direct', direct.toString(), 365);
            setCookie('openfaasurl', openfaasUrl, 365);
            setCookie('noredges', noredges.toString(), 365);
            setCookie('theme', theme, 365);
            FUNCTIONCALL = newOpenfaasUrl;
            location.reload(true);
        }
        $('#url-spinner').removeClass('hidden');
        $('#url-message').addClass('hidden');
        if($('#no-openfaas-checkbox').prop('checked') == false){
            // check if valid
            fetch('/check_connection', { method: 'POST', body: JSON.stringify({ url: openfaasUrl }) }).then(data => data.json()).then(data => {
                if (data.success) {
                    onSuccess();
                }else{
                    $('#url-spinner').addClass('hidden');
                    $('#url-message').removeClass('hidden');
                }
            }).catch(function(){
                $('#url-spinner').addClass('hidden');
                $('#url-message').addClass('hidden');
                $('#dismiss-url-modal-btn').click();
                showInfo('Could not connect to server', 'red');
            });
        }else{
            onSuccess();
        }
    });

    $('#no-openfaas-checkbox').change(function() {
        if($(this).prop('checked') == true){
            $('#url-input').prop('disabled', true);
            $('#direct-checkbox').prop('disabled', true);
        }else{
            $('#url-input').prop('disabled', false);
            $('#direct-checkbox').prop('disabled', false);
        }
    }); 

    $('#restore-defaults-btn').on('click', function(){
        setCookie('direct', direct.toString(), -1);
        setCookie('openfaasurl', openfaasUrl, -1);
        localStorage.removeItem('last_host');
        location.reload(); 
    });

    setCookie('openfaasurl', openfaasUrl, 365);
    
    if (openfaasUrl === 'None'){
        FUNCTIONCALL = '/local';
        $('#direct-checkbox').prop('disabled', true);
        $('#no-openfaas-checkbox').prop('checked', true);
    }else if (direct){
        if (openfaasUrl.slice(-1) == '/'){
            openfaasUrl = openfaasUrl.slice(0, -1);
        }
        FUNCTIONCALL = `${openfaasUrl}/function/${functionName}`;
        $('#direct-checkbox').prop('disabled', false);
        $('#direct-checkbox').prop('checked', true);
    }

    if($('#no-openfaas-checkbox').prop('checked') == true){
        openfaasUrl = 'None';
        $('#url-input').prop('disabled', true);
    }else{
        $('#url-input').prop('disabled', false);
    }
    if(WEBSOCKET){
        socket = io();
        socketIntv = setInterval(function () {
            socket.emit('server_stats');
        }, 1000);
        socket.emit('server_stats');
        socket.on('server_stats', function (msg) {
            if (msg != null){
                if (!IsJsonString(msg.data)) return;
                data = JSON.parse(msg.data);
                if (data != null) {
                    if (data.success){
                        $('#running-tests-label').text(data.count);
                    }
                }else if(data.stop){
                    clearInterval(socketIntv);
                }
            }
        });
    }
});