function CreateTest(id, users, spawnRate, host, time, date){
    var test = document.createElement('div');
    test.setAttribute('id', id);
    const template = ```
    <div class="card">
        <div class="card-header">
            <div class="row">
                <div class="col-2">Id:${id}</div>
                <div class="col-2">Users:${users}</div>
                <div class="col-2">Spawn rate:${spawnRate}</div>
                <div class="col-2">Host:${host}</div>
                <div class="col-2">${date}</div>
                <div class="col-2">${time}</div>
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
    ```;
    test.innerHTML = template;
    $(test).find('.start-test').on('click', function(){
        console.log('start')
    });
    $(test).find('.stop-test').on('click', function(){
        console.log('stop')
    });
    $(test).find('.download-test').on('click', function(){
        console.log('download')
    });
    return test;
}

function createRow(){

}

window.onload = function () {
    const usersInput = $('#users-input');
    const spawnRateInput = $('#spawn-rate-input');
    const hostInput = $('#host-input');
    const timeInput = $('#time-input');
    const fileInput = $('#file-input');
    const deployBtn = $('#deploy-btn');

    deployBtn.on('click', function(){
        const users = usersInput.val();
        const spawnRate = spawnRateInput.val();
        const host = hostInput.val();
        const time = timeInput.val();
        // get the file, read the file, store it in code
        const file = fileInput.val();

        // post users, spawn rate, host, time, code
        // fetch().then().catch();
        // get id -> create test
        console.log("deploy: ", users, spawnRate, host, time);
        return false;
    });
}   