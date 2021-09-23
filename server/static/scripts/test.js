document.addEventListener("DOMContentLoaded", function () {
    const id = document.getElementById('test-id').innerText;
    function callBack(res) {
        if (res.success) {
            const data = res.data;
            var users = null;
            var spawn_rate = null;
            var host = null;
            var time = null;
            const info = JSON.parse(data.info);
            if (info != null) {
                users = info.users;
                spawn_rate = info.spawn_rate;
                host = info.host;
                date = info.date;
                time = info.time;
            }
            const test = CreateTest(data.id, users, spawn_rate, host, time, data.status, data.code, data.data, data.valid, data.started_at);
            document.getElementById('content').appendChild(test);
        }
    }
    if (DIRECT) {
        fetch(FUNCTIONCALL, { method: 'POST', body: JSON.stringify({ command: 8, id: id }) }).then(res => res.json()).then(res => {
            callBack(res);
        }).catch();
    } else {
        fetch('/test-info/' + id, { method: 'POST' }).then(res => res.json()).then(res => {
            callBack(res);
        }).catch();
    }
});