FUNCTIONCALL = '';

function CreateTest(id, users, spawnRate, host, time, status, code, stats, valid, startedAt){
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
        <button type="button" class="btn btn-primary start-test">
            Start
        </button>
        <button type="button" class="btn btn-primary stop-test" disabled>
            Stop
        </button>
        <button type="button" class="btn btn-primary download-test" disabled>
            Download
        </button>
        <button type="button" class="btn btn-danger delete-test">Delete</button>
    </div>
    `;

    test.innerHTML = template;
    const idCol = $(test).find('.test-id');
    const startBtn = $(test).find('.start-test');
    const stopBtn = $(test).find('.stop-test');
    const downloadBtn = $(test).find('.download-test');
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


    if (status == 0){ // not deployed
        if (valid === false){
            notValid.removeClass('hidden');
            idCol.addClass('red');
        }else{
            check.removeClass('hidden');
        }
        startBtn.prop("disabled",true);
        stopBtn.prop("disabled",true);
        downloadBtn.prop("disabled",false);
    }

    if (status == 1){ // running 
        idCol.addClass('green');
        startBtn.prop("disabled",true);
        stopBtn.prop("disabled",false);
        downloadBtn.prop("disabled",true);
        elapsed.removeClass('hidden');
        spinner.removeClass('hidden');
        // get updates

        eventSource = new EventSource('/stream/' + id);
        eventSource.onmessage = function (e) {
            if(!IsJsonString(e.data)) return;
            message = JSON.parse(e.data)
            interpretMessage(message);
        };
    }
    if (status == 2){ // deployed
        idCol.addClass('orange');
        startBtn.prop("disabled",false);
        stopBtn.prop("disabled",true);
        downloadBtn.prop("disabled",true);
    }

    startBtn.on('click', function(){
        fetch('/start/'+ id, {method: 'POST'}).then(data => data.json()).then(data => {
            console.log(data);
            if (data.success){
                idCol.removeClass('orange').addClass('green');
                spinner.removeClass('hidden');
                elapsed.removeClass('hidden');                                      
                elapsedText.text('pending');
                $(this).prop("disabled",true);
                stopBtn.prop("disabled",false);
    
                if (startedAt == null){
                    startedAt = Date.now()/1000;
                }
                eventSource = new EventSource('/stream/' + id);
                eventSource.onmessage = function (e) {
                    if(!IsJsonString(e.data)) return;
                    message = JSON.parse(e.data)
                    interpretMessage(message);
                };  
            }else{
                if (data.exit_code == 5){
                    showInfo('Too many tests are running. Pleas stop or delete a running test');
                }
            }
                            
        });

    });

    stopBtn.on('click', function(){
        fetch('/stop/'+ id, {method: 'POST'}).then(data => data.json()).then(data => {
            if (data.success){
                idCol.removeClass('orange').removeClass('green').removeClass('red');
                clearInterval(intv);
                check.removeClass('hidden');
                spinner.addClass('hidden');
                $(this).prop("disabled",true);
                downloadBtn.prop("disabled",false);
                eventSource.close();
            }else{
                showInfo('There was an error stopping the test');
            }

        });

    });

    downloadBtn.on('click', function(){
        var xhr = new XMLHttpRequest();
        xhr.open("POST", FUNCTIONCALL);
        xhr.responseType = "arraybuffer";
        xhr.onload = function () {
            if (this.status === 200) {
                var blob = new Blob([xhr.response], {type: "application/zip"});
                var objectUrl = URL.createObjectURL(blob);
                window.location.href = objectUrl;
            }
        };
        xhr.send('{"command":5 ,"id":"'+id+'"}');
    });

    deleteBtn.on('click', function(){
        let formData = new FormData();
        formData.append('ids', '["'+id+'"]');
        setConfirmationModal(id + ' Are you sure you want to delete this test?', function() {
            fetch('/delete', { method: 'POST', body: formData }).then(data => {
                $('#dismiss-confirmation-modal-btn').click();
                $(test).remove();
                if (eventSource != null) eventSource.close();
             }).catch();
        });
        return false;
    });

    if (stats != null){
        const jData = JSON.parse(stats)
        update(jData);
    }

    codeLink.on('click', function(){
        setUpCode(code);
    });

    function interpretMessage(message){
        if (message.success){
            if (message.status == 0){
                // test is not running
                clearInterval(intv);
                idCol.removeClass('orange').removeClass('green').removeClass('red');
                check.removeClass('hidden');
                spinner.addClass('hidden');
                stopBtn.prop("disabled",true);
                downloadBtn.prop("disabled",false);
                eventSource.close();
                return;
            }
            if (!intvSet){
                intv = setInterval(function(){ 
                    elapsedText.text(parseInt((Date.now()/1000) - startedAt));
                }, 1000);
                intvSet = true;
            }
            const jData = JSON.parse(message.data)
            update(jData);
        }else{
            if(message.exit_code == 4){
                showInfo(id + 'There was an error running your locust file');
                clearInterval(intv);
                idCol.removeClass('orange').removeClass('green').addClass('red');
                notValid.removeClass('hidden');
                elapsed.addClass('hidden');
                spinner.addClass('hidden');
                startBtn.prop("disabled",true);
                stopBtn.prop("disabled",true);
                downloadBtn.prop("disabled",true);
                eventSource.close();
                return;
            }
        }
    }
    // update results
    function update(jData){
        footer.children().remove();
        results.children().remove();
        for (var i = 0; i < jData.length; i++){
            var type = jData[i]["Type"];
            const name = jData[i]["Name"];
            const requests = jData[i]["Request Count"];
            const fails = jData[i]["Failure Count"];
            const med = jData[i]["Median Response Time"];
            const avg =  jData[i]["Average Response Time"].toString().slice(0, 8);
            const min =  jData[i]["Min Response Time"].toString().slice(0, 8);
            const max =  jData[i]["Max Response Time"].toString().slice(0, 8);
            const avgSize =  jData[i]["Average Content Size"].toString().slice(0, 8);
            const rps =  jData[i]["Requests/s"].toString().slice(0, 8);
            const fps =  jData[i]["Failures/s"].toString().slice(0, 8);
            if (i == jData.length -1){
                type = '';
                footer.append(createRow(type, name, requests, fails, med, avg, min, max, avgSize, rps, fps));
            }else{
                results.append(createRow(type, name, requests, fails, med, avg, min, max, avgSize, rps, fps));
            }
        }
    }

    return test;
}

function createRow(type, name, requests, fails, med, avg, min, max, avgSize, rps, fps){
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

function showInfo(message){
    // set message
    $('#info-message').text(message);
    // show message
    $('#info-modal-button').click();
}

function setUpCode(code){
    // set code
    $('#code').text(code);
    // show code
    $('#code-modal-button').click(); 
}

function setConfirmationModal(message, func){
    // set message
    $('#confirm-message').text(message);
    // unbind
    $('#confirm-delete').off('click');
    // bind
    $('#confirm-delete').on('click', function(){
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
    FUNCTIONCALL = document.getElementById('function-call').innerText
});