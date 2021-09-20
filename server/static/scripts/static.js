function CreateTest(id, users, spawnRate, host, status, code, stats){
    var test = document.createElement('div');
    test.setAttribute('id', id);
    const template = `
    <div class="card">
        <div class="card-header">
            <div class="row">
                <div class="col-2">${id}</div>
                <div class="col-2">Users: ${users}</div>
                <div class="col-2">Spawn rate: ${spawnRate}</div>
                <div class="col-2">Host: ${host}</div>
                <div class="col-1">
                    <i class="far fa-file-alt code"></i>
                </div>
                <div class="col-2 elapsed hidden">elapsed: <label class="elapsed-text">pending</label></div>
                <div class="col-1">
                    <div class="spinner-border text-primary spinner hidden"></div>
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
    <div class="buttons">
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
    const startBtn = $(test).find('.start-test');
    const stopBtn = $(test).find('.stop-test');
    const downloadBtn = $(test).find('.download-test');
    const deleteBtn = $(test).find('.delete-test');
    const spinner = $(test).find('.spinner');
    const elapsed = $(test).find('.elapsed');
    const elapsedText = $(test).find('.elapsed-text');
    const codeLink = $(test).find('.code');
    var intv;
    var eventSource;

    if (status == 0){ // not deployed
        startBtn.prop("disabled",true);
        stopBtn.prop("disabled",true);
        downloadBtn.prop("disabled",false);
    }

    if (status == 1){ // running 
        startBtn.prop("disabled",true);
        stopBtn.prop("disabled",false);
        downloadBtn.prop("disabled",true);
        spinner.removeClass('hidden');
        // get updates
        var elapsedTime = 0;
        eventSource = new EventSource('/stream/' + id);
        eventSource.onmessage = function (e) {
            if(!IsJsonString(e.data)) return;
            message = JSON.parse(e.data)
            if (message.success){
                if (message.status == 0){
                    // test is not running
                    spinner.addClass('hidden');
                    clearInterval(intv);
                    stopBtn.prop("disabled",true);
                    downloadBtn.prop("disabled",false);
                    eventSource.close();
                    return;
                }
                if (elapsedTime == 0){
                    intv = setInterval(function(){ 
                        elapsedText.text(elapsedTime);
                        elapsedTime = elapsedTime + 1;
                    }, 1000);
                }
                const jData = JSON.parse(message.data);
                update(jData);
            }else{
                if(message.exit_code == 4){
                    showInfo(id + 'There was an error running your locust file');
                    clearInterval(intv);
                    spinner.addClass('hidden');
                    startBtn.prop("disabled",true);
                    stopBtn.prop("disabled",true);
                    downloadBtn.prop("disabled",true);
                    eventSource.close();
                    return;
                }
            }
        };
    }
    if (status == 2){ // deployed
        startBtn.prop("disabled",false);
        stopBtn.prop("disabled",true);
        downloadBtn.prop("disabled",true);
    }

    const results = $(test).find('.card-body > .results');
    const footer = $(test).find('.card-footer');

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

    startBtn.on('click', function(){
        fetch('/start/'+ id, {method: 'POST'});
        spinner.removeClass('hidden');
        elapsed.removeClass('hidden');
        var elapsedTime = 0;

        $(this).prop("disabled",true);
        stopBtn.prop("disabled",false);

        eventSource = new EventSource('/stream/' + id);
        eventSource.onmessage = function (e) {
            if(!IsJsonString(e.data)) return;
            message = JSON.parse(e.data)
            if (message.success){
                if (message.status == 0){
                    // test is not running
                    spinner.addClass('hidden');
                    clearInterval(intv);
                    stopBtn.prop("disabled",true);
                    downloadBtn.prop("disabled",false);
                    eventSource.close();
                    return;
                }
                if (elapsedTime == 0){
                    intv = setInterval(function(){ 
                        elapsedText.text(elapsedTime);
                        elapsedTime = elapsedTime + 1;
                    }, 1000);
                }
                const jData = JSON.parse(message.data)
                update(jData);
            }else{
                if(message.exit_code == 4){
                    showInfo(id + 'There was an error running your locust file');
                    clearInterval(intv);
                    spinner.addClass('hidden');
                    startBtn.prop("disabled",true);
                    stopBtn.prop("disabled",true);
                    downloadBtn.prop("disabled",true);
                    eventSource.close();
                    return;
                }
            }
        };
    });

    stopBtn.on('click', function(){
        fetch('/stop/'+ id, {method: 'POST'});
        clearInterval(intv);
        spinner.addClass('hidden');
        $(this).prop("disabled",true);
        downloadBtn.prop("disabled",false);
        eventSource.close();
    });

    downloadBtn.on('click', function(){
        console.log('download')
    });

    deleteBtn.on('click', function(){
        let formData = new FormData();
        formData.append('ids', '["'+id+'"]');
        setConfirmationModal(id + ' Are you sure you want to delete this test?', function() {
            fetch('/delete', { method: 'POST', body: formData }).then(data => {
                $('#dismiss-confirmation-modal-btn').click();
                $(test).remove();
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