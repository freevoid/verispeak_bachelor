$(document).ready(function () {
    console.log("Configuring upload..");
    uploadedCount = 0;
    uploadedTime = 0.0;
    MIN_UTTERANCE_LENGTH = 1.5;
});

function recordAppletLoaded () {
    console.log("Applet loaded.");
    window.recorder = document.ListenUpRecorder;
    recorder.setUploadCompletionScript("uploadCompleted();");
    recorder.setUploadFailureScript("uploadFailed();");
}

function canSendToVerification () {
    // Checks all conditions that must be met to verificate utterance
    // such as minimal length
    return (recorder.isPlayable() && recorder.getMaxPlayableTime() > MIN_UTTERANCE_LENGTH);
}

function recordStateChanged (from, to) {
    console.log("State changed:", from, "=>", to);
    if (from=='recording' && to=='stopped') {
        console.log("Recorded utterance, going to send..");
        if (canSendToVerification()) {
            setLoading("Запись отправляется на сервер..");
            recorder.sendRecordedMessage();
        } else {
            waitForDataState(verificationBlock);
        }
    }
}

function setLoading(message) {
    currentUploadingTime = recorder.getMaxPlayableTime();
    getContent(verificationBlock).html(
        '<img src="/media/img/loading.gif" id="id_loading_img" /><span class="loadingMessage">' + message + '</span>'
    );
}

function unsetLoading() {
    clearContent(verificationBlock);
}

function uploadCompleted () {
    console.log("Uploaded!");
    window.uploadedCount += 1;
    window.uploadedTime += window.currentUploadingTime;
    unsetLoading();
}

function uploadFailed () {
    console.log("Upload failed:(");
    unsetLoading();
}

function toggleRecording (this_) {
    console.log("Toggle recording..");
    var recorder = document.ListenUpRecorder;
    if (recorder.isRecording()) {
        recorder.stopAudio();
        $(this_).val("Запись");
    } else {
        recorder.record();
        $(this_).val("Стоп");
    }
}

function confirmVerification (url, form) {
    console.log("Proceeding to verification..");
    $.post(url, form.serializeArray(),
            function (data) {
                console.log("Got response:", data);
                if (data.result == 0) { // all ok
                    setTimeout(monitorProgress, 1500);
                } else {
                    // XXX response parsing + client notifying
                }
            }, "json");
}

function getContent(verificationBlock) {
    return verificationBlock.find(".voice_auth_content");
}

function clearContent(verificationBlock) {
    getContent(verificationBlock).html('');
}

function waitForDataState(verificationBlock) {
    getContent(verificationBlock).html('<p class="note">' +
        'Голосовых данных недостаточно для аутентификации. Пожалуйста, запишите ещё один образец.' +
        '</p>');
}

function monitorProgress () {
    console.log("Monitoring..");
    $.get(monitorURL, {},
        function (data) {
            console.log("Monitor state:", data.result, data.message);

            var code = data.result;
            if (code == 0) {
                var state = data.message;
                if (state == "verification_success") {
                    console.log("Verificated!")
                } else if (state == "verification_failed") {
                    console.log("Access denied!")
                } else if (state == "waiting_for_data") {
                    waitForDataState(verificationBlock);
                } else if (state == "failed") {
                } else if (state == "canceled") {
                } else {
                    setTimeout(monitorProgress, 1500);
                }
            } else {
                alert("Unexpected error occured:", data);
            }
        }, "json");
}

