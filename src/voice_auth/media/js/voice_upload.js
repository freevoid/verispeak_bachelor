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
    initialState(verificationBlock);
}

function canSendToVerification () {
    // Checks all conditions that must be met to verificate utterance
    // such as minimal length
    console.log('Recorded (is sec.):', recorder.getMaxPlayableTime());
    return (recorder.isPlayable() && recorder.getMaxPlayableTime() > MIN_UTTERANCE_LENGTH);
}

function recordStateChanged (from, to) {
    console.log("State changed:", from, "=>", to);
    if (from=='recording' && to=='paused') {
        console.log("Recorded utterance, going to send..");
        if (canSendToVerification()) {
            recorder.stopAudio();
            setLoading("Запись отправляется на сервер..");
            recorder.sendRecordedMessage();
        } else {
            pasteNote(verificationBlock,
                    sprintf('Записан слишком короткий образец (%.2f сек.). Повторите запись ещё раз.',
                        recorder.getMaxPlayableTime()));
            maskButtons(verificationBlock, true, true);
        }
    }
}

function getContent(verificationBlock) {
    return verificationBlock.find(".voice_auth_content");
}

function clearContent(verificationBlock) {
    getContent(verificationBlock).html('');
}

function getSessionContext(verificationBlock) {
    return verificationBlock.find("form").serializeArray();
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
    confirmVerification(confirmURL, getSessionContext(verificationBlock));
}

function uploadFailed () {
    console.log("Upload failed:(");
    unsetLoading();
    failedState("Возникла ошибка при отправке записи на сервер");
}

function toggleRecording (this_) {
    console.log("Toggle recording..");
    var recorder = document.ListenUpRecorder;
    if (recorder.isRecording()) {
        recorder.pauseAudio();
        $(this_).val("Запись");
    } else {
        recorder.record();
        $(this_).val("Стоп");
        recordingState(verificationBlock);
    }
}

function confirmVerification (url, data) {
    console.log("Proceeding to verification..");
    $.post(url, data,
            function (data) {
                console.log("Got response:", data);
                if (data.result == 0) { // all ok
                    verificationState(verificationBlock);
                    setTimeout(monitorProgress, 1500);
                } else {
                    alert("Необработанная ошибка:", data);
                    // XXX response parsing + client notifying
                }
            }, "json");
}

function pasteNote(verificationBlock, note) {
    getContent(verificationBlock).html('<span class="note">' + note + '</span>');
}

function pasteError(verificationBlock, note) {
    getContent(verificationBlock).html('<span class="errornote">' + note + '</span>');
}

function waitForDataState(verificationBlock) {
    state = "waiting_for_data";
    pasteNote(verificationBlock,
            'Голосовых данных недостаточно для аутентификации. Пожалуйста, запишите ещё один образец.');
    maskButtons(verificationBlock, true, true);
}

function verificationState(verificationBlock) {
    state = "verification";
    setLoading("Подождите, идёт процесс верификации..");
    maskButtons(verificationBlock, false, false);
}

function setButtonEnabled(verificationBlock, selector, is_enabled) {
    if (is_enabled) {
        verificationBlock.find(selector).removeAttr("disabled");
    } else {
        verificationBlock.find(selector).attr("disabled", "true");
    }
}

function maskButtons(verificationBlock, record_mask, cancel_mask) {
    setButtonEnabled(verificationBlock, "#id_record_button", record_mask);
    setButtonEnabled(verificationBlock, "#id_cancel_button", cancel_mask);
}

function initialState(verificationBlock) {
    state = "initial";
    pasteNote(verificationBlock, "Нажмите кнопку ``Запись'', произнесите ключевую фразу, и нажмите на кнопку ``Стоп''.");
    maskButtons(verificationBlock, true, true);
}

function failedState(verificationBlock, reason) {
    state = "failed";
    pasteError(verificationBlock, reason +
            '. Попробуйте ещё раз. Если ошибка возникает снова, обратитесь в службу поддержки.');
    maskButtons(verificationBlock, false, true);
}

function accessDeniedState(verificationBlock) {
    state = "verification_failed";
    console.log("Access denied!");
    pasteError(verificationBlock, "Аутентификация завершилась неудачно. Попробуйте ещё раз или воспользуйтесь обычным способом, нажав кнопку ``Возврат''.");
    maskButtons(verificationBlock, false, true);
}

function recordingState(verificationBlock) {
    state = "recording";
    pasteNote(verificationBlock, "Идёт запись..");
    maskButtons(verificationBlock, true, false);
}

function monitorProgress() {
    console.log("Monitoring..");
    $.get(monitorURL, getSessionContext(verificationBlock),
        function (data) {
            console.log("Monitor state:", data.result, data.message);

            var code = data.result;
            if (code == 0) {
                var state = data.message;
                if (state == "verification_success") {
                    console.log("Verificated!")
                    window.location = redirectURL;
                } else if (state == "verification_failed") {
                    accessDeniedState(verificationBlock);
                } else if (state == "waiting_for_data") {
                    waitForDataState(verificationBlock);
                } else if (state == "failed") {
                    failedState(verificationBlock, "В процессе верификации возникла ошибка");
                } else if (state == "canceled") {
                    canceledState(verificationBlock);
                } else {
                    setTimeout(monitorProgress, 1500);
                }
            } else {
                alert("Unexpected error occured:", data);
            }
        }, "json");
}

function cancelVerification() {
    if (state == "waiting_for_data") {
        $.post(cancelURL, getSessionContext(verificationBlock),
                function (data) {
                    if (data.result == 0) {
                        window.location = fallbackURL;
                    } else {
                        alert(data);
                    }
                }, "json");
    } else if (state == "failed") {
        window.location = fallbackURL;
    } else if (state == "initial") {
        window.location = fallbackURL;
    }
}

