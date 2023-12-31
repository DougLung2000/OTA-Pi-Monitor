$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    // var numbers_received = 00000;

    //receive details from server
    socket.on('newdata', function(msg) {
        console.log("Received new data" + msg.SignalData);
        //maintain a list of ten numbers
        //if (numbers_received.length >= 10){
        //     numbers_received.shift()
        //}            
//        data_received = (msg.SignalData);
//        data_string = '';
        data_string = '<p>' + msg.SignalData + '</p>';
        $('#log').html(data_string);
    });

});
