$(document).ready(function () {
    console.log("Configuring upload..");
});

function recordAppletLoaded () {
    console.log("Applet loaded.");
    var recorder = document.ListenUpRecorder;
    recorder.setUploadCompletionScript("uploadCompleted();");
    recorder.setUploadFailureScript("uploadFailed();");
}

function recordStateChanged (from, to) {
    console.log("State changed:", from, "=>", to);
    if (from=='recording' && to=='stopped') {
        console.log("Recorded utterance, going to send..");
        var recorder = document.ListenUpRecorder;
        if (recorder.isPlayable()) {
            recorder.sendRecordedMessage();
        }
    }
}

function uploadCompleted () {
    console.log("Uploaded!");
}

function uploadFailed () {
    console.log("Upload failed:(");
}

