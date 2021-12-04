document.addEventListener("DOMContentLoaded", function () {
    var check = false;
    if(document.getElementById('check').innerText == "true") check = true;
    console.log(check);
    if(check){
        var eventSource;
        var socketIntv;
        if (WEBSOCKET){
            socketIntv = setInterval(function () {
                socket.emit('openfaas');
            }, 1000);
            socket.on('openfaas', function (msg) {
                if (!IsJsonString(msg.data)) return;
                var message = JSON.parse(msg.data);
                console.log(message)
            });
        }else{
            eventSource = new EventSource('/openfaas-stream');
            eventSource.onmessage = function (e) {
                var message = JSON.parse(e.data);
                var installed = message.installed;
                console.log(installed);
            };
        }
    }
});

