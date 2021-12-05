document.addEventListener("DOMContentLoaded", function () {
    var check = false;
    if(document.getElementById('check').innerText == "true") check = true;
    console.log(check);
    if(check){
        $('#initializing').removeClass('hidden');
        var eventSource;
        if (WEBSOCKET){
            socket.emit('openfaas');
            socket.on('openfaas', function (msg) {
                var message = JSON.parse(msg.data);
                if (message == true){
                    $('#message').text('function installed');
                    $('#initializing').addClass('hidden');
                }
                console.log(message)
            });
        }else{
            eventSource = new EventSource('/openfaas_stream');
            eventSource.onmessage = function (e) {
                var message = JSON.parse(e.data);
                var installed = message.installed;
                if (installed == true){
                    $('#message').text('function installed');
                    $('#initializing').addClass('hidden');
                }
                console.log(installed);
            };
        }
    }
});

