// supporting code for SGF uploads
function sgf_upload_start(event) {
    event.stopPropagation();
    event.preventDefault();
    var input_file = document.getElementById('sgf_upload_file');
    input_file.click();
};
function sgf_upload_go(input_file) {
    if(input_file.files.length < 1) { return; }

    var file = input_file.files[0];
    if(file.size > 1024*1024) {
        window.alert("File is too large (max 1MB).");
        return;
    }
    var reader = new FileReader();

    // clear the files list so that user can re-upload a file by the same name,
    // and onchange will still fire.
    input_file.value = '';

    reader.onload = function(evt) {
       uploadSGFXHR(evt.target.result);
    };
    reader.readAsText(file);
}
