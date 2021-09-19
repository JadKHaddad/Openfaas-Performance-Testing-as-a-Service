window.onload = function () {
    const id = document.getElementById('test-id').innerText;
    fetch('/test-info/'+id, { method: 'POST'}).then(data => data.json()).then(data => {
        if (data.success){
            var users = null;
            var spawn_rate = null;
            var host = null;
            var time =  null;
            const info = JSON.parse(data.data.info);
            if (info != null){
                users = info.users;
                spawn_rate = info.spawn_rate;
                host = info.host;
                date = info.date;
            }
            const test = CreateTest(data.data.id, users, spawn_rate, host, data.data.status, data.data.code, data.data.data);
            document.getElementById('content').appendChild(test);
        }
    }).catch();
}