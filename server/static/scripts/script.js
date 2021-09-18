function CreateTest(id, users, spawnRate, host, date){
    var test = document.createElement('div');
    test.setAttribute('id', id);
    const template = `
    <div class="card">
        <div class="card-header">
            <div class="row">
                <div class="col-2">${id}</div>
                <div class="col-1">Users: ${users}</div>
                <div class="col-2">Spawn rate: ${spawnRate}</div>
                <div class="col-2">Host: ${host}</div>
                <div class="col-2">${date}</div>
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
        </div>
        <div class="card-footer">
            <div class="container-fluid">
                <div class="row">
                    <div class="col-1"></div>
                    <div class="col-2">Aggregated</div>
                    <div class="col-1">/</div>
                    <div class="col-1">/</div>
                    <div class="col-1">/</div>
                    <div class="col-1">/</div>
                    <div class="col-1">/</div>
                    <div class="col-1">/</div>
                    <div class="col-1">/</div>
                    <div class="col-1">/</div>
                    <div class="col-1">/</div>
                </div>
            </div>
        </div>
    </div>
    <div class="buttons">
        <button type="button" class="btn btn-primary start-test">
            Start
        </button>
        <button type="button" class="btn btn-primary stop-test">
            Stop
        </button>
        <button type="button" class="btn btn-primary download-test">
            Download
        </button>
    </div>
    `;
    test.innerHTML = template;
    const startBtn = $(test).find('.start-test');
    const stopBtn = $(test).find('.stop-test');
    const downloadBtn = $(test).find('.download-test');
    const spinner = $(test).find('.spinner');
    const elapsed = $(test).find('.elapsed');
    const elapsedText = $(test).find('.elapsed-text');
    var intv;
    const eventSource = new EventSource('/stream/' + id);
    stopBtn.prop("disabled",true);
    downloadBtn.prop("disabled",true);

    startBtn.on('click', function(){
        fetch('/start/'+ id, {method: 'POST'});
        spinner.removeClass('hidden');
        elapsed.removeClass('hidden');
        var elapsedTime = 0;

        $(this).prop("disabled",true);
        stopBtn.prop("disabled",false);

        eventSource.onmessage = function (e) {
            message = JSON.parse(e.data)
            if (message.success){
                if (elapsedTime == 0){
                    intv = setInterval(function(){ 
                        elapsedText.text(elapsedTime);
                        elapsedTime = elapsedTime + 1;
                    }, 1000);
                }
                const jData = JSON.parse(message.data)
                for (var i = 0; i < jData.length; i++){
                    console.log(
                        'Type: ', jData[i]["Type"],
                        'Name: ', jData[i]["Name"],
                        'Request Count: ', jData[i]["Request Count"],
                        'Failure Count: ', jData[i]["Failure Count"],
                        'Median Response Time: ', jData[i]["Median Response Time"],
                        'Average Response Time: ', jData[i]["Average Response Time"],
                        'Min Response Time: ', jData[i]["Min Response Time"],
                        'Max Response Time: ', jData[i]["Max Response Time"],
                        'Average Content Size: ', jData[i]["Average Content Size"],
                        'Requests/s: ', jData[i]["Requests/s"],
                        'Failures/s: ', jData[i]["Failures/s"]
                    );
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
    return test;
}

function createRow(){

}

function formatDate(date, format) {
    const map = {
        mm: date.getMonth() + 1,
        dd: date.getDate(),
        yy: date.getFullYear().toString().slice(-2),
        yyyy: date.getFullYear()
    }

    return format.replace(/mm|dd|yy|yyy/gi, matched => map[matched])
}

window.onload = function () {
    const deployBtn = $('#deploy-btn');
    var code = '';
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

    deployBtn.on('click', function(){
        const users = $('#users-input').val();
        const spawnRate = $('#spawn-rate-input').val();
        const host = $('#host-input').val();
        const time = $('#time-input').val();
        let formData = new FormData();
        formData.append('users', users);
        formData.append('spawn_rate', spawnRate);
        formData.append('host', host);
        formData.append('time', time);
        formData.append('code', code);

        fetch('/deploy', { method: 'POST', body: formData }).then(data => data.json()).then(data => {
            if (data.success){
                const id = data.id;
                const today = new Date();
                const date = formatDate(today, 'dd.mm.yyyy');
                const test = CreateTest(id, users, spawnRate, host,date);
                document.getElementById('content').appendChild(test);
            }
        }).catch();
        
        // get id -> create test
        //console.log(requestJson);
        return false;
    });
}   