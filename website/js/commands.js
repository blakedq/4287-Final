
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
                $('#result').text(' succeeded with   ' + msg['exec_time'] + 's');
            }
            else {
                $('#result').text(' ' + msg['status']);
            }

            $('#stdout').text(msg['output'] + '\n' + msg['error_msg']);
        }
    });

    console.log('done')
})
