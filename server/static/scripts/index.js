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
    var eventSource;
    stopBtn.prop("disabled",true);
    downloadBtn.prop("disabled",true);

    startBtn.on('click', function(){
        fetch('/start/'+ id, {method: 'POST'});
        spinner.removeClass('hidden');
        elapsed.removeClass('hidden');
        var elapsedTime = 0;

        $(this).prop("disabled",true);
        stopBtn.prop("disabled",false);

        eventSource = new EventSource('/stream/' + id);
        eventSource.onmessage = function (e) {
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
                const results = $(test).find('.card-body > .results');
                const footer = $(test).find('.card-footer');
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
        return false;
    });

    // deploy a test for debugging
    const users = 4;
    const spawnRate = 6;
    const host = 'https://google.com';
    const time = 90;
    code = "from locust import HttpUser, task, between\nclass User(HttpUser):\n    wait_time = between(1, 5)\n    host = \"https://google.com\"\n\n    @task\n    def my_task(self):\n        self.client.get(\"/\")\n\n    @task\n    def task_404(self):\n        self.client.get(\"/non-existing-path\")\n\n";
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
}   