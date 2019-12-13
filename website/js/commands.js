
// const serverUrl = 'http://localhost:8888';
const serverUrl = 'http://ec2-3-90-220-109.compute-1.amazonaws.com:8888';
const id = 1;
// let editor = ace.edit("editor");


$('#execute').on("click", function() {
    codeData = {
        id: id, 
        timeout: 5, 
        code: editor.getValue(), 
        input: ''
    }; 

    console.log(editor.getValue());

    $.ajax({
        url: serverUrl + '/execute',
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(codeData),
        dataType: 'json',
        // async: true,
        success: function(msg) {
            console.log(msg);

            if (msg['status'] == 'success') {
                let mstime = (msg['exec_time'] * 1000).toFixed(3);
                $('#result').text(' succeeded with   ' + mstime + 'ms');
            }
            else {
                $('#result').text(' ' + msg['status']);
            }

            $('#stdout').html(msg['output'].replace(/\n/g, "<br>") + msg['error_msg'].replace(/\n/g, "<br>"));
        }
    });

    console.log('done')
})
