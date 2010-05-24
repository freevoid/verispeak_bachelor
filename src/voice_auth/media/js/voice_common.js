function StateMachine (transitionTable) {
    this.transitionTable = transitionTable;

    // Main FSM function: search for action in transitionTable depending
    // on current state
    this.event = function (event_, args) {
        console.log("GOT EVENT:", event_, "STATE:", this.state);
        var actions = this.transitionTable[event_];
        if (typeof(actions) != "undefined") {
            action = actions[this.state];
            if (typeof(action) != "undefined") {
                console.log("Calling action", action);
                this[action].call(this, args);
            } else {
                console.log("No transition:", event_, this.state);
            }
        } else {
            console.log("Unrecognized event:", event_);
        }
    };
};

function BaseVoiceBlock (selector, params, urls, defer_creation) {
    if (typeof(selector) == "undefined") { return }

    // CONSTANTS
    
    this.UPLOAD_COMPLETED_GLOBAL_NAME = "BaseVoiceBlock_uploadCompleted";
    this.UPLOAD_FAILED_GLOBAL_NAME = "BaseVoiceBlock_uploadFailed";

    transitionTable = {
        created: {undefined: "to_initial"},
        record: {
            initial: "to_recording",
            insufficient_to_upload: "to_recording"
        },
        pause: {recording: "to_pausing"},
        paused: {pausing: "to_paused"},

        ready_to_upload: {paused: "to_uploading"},
        too_short_to_upload: {paused: "to_insufficient_to_upload"},
        upload_failed: {uploading: "to_upload_failed"},
        upload_completed: {uploading: "to_upload_completed"},
        cancel: {
            initial: "return_back",
            insufficient_to_upload: "return_back",
            failed_to_upload: "return_back"
        }
    }
    StateMachine.call(this, transitionTable);

    console.log("Init BaseVoiceBlock", selector, params, urls);
    
    // PUT GLOBAL CALLBACKS

    this.uploadCompleted = function () {
        console.log("Uploaded!");
        this_.event("upload_completed");
    };

    this.uploadFailed = function () {
        console.log("Upload failed:(");
        this_.event("upload_failed");
    };

    var this_ = this;
    this.appletReadyScript = function () {
        console.log("Applet loaded", this_);
        this_.applet = document[params.appletName];
        window[this_.UPLOAD_COMPLETED_GLOBAL_NAME] = this_.uploadCompleted;
        window[this_.UPLOAD_FAILED_GLOBAL_NAME] = this_.uploadFailed;
        this_.applet.setUploadCompletionScript(this_.UPLOAD_COMPLETED_GLOBAL_NAME + '();');
        this_.applet.setUploadFailureScript(this_.UPLOAD_FAILED_GLOBAL_NAME + '();');

        this_.event("applet_loaded");
    };

    this.recordStateChanged = function (from, to) {
        // handle applet state changing and call
        // appropriate callback method, if defined
        console.log("State changed:", from, "=>", to);
        var callback_name = "record_" + from + "_to_" + to;
        if (typeof(this_[callback_name]) != "undefined") {
            this_[callback_name].call(this_);
        }
    };

    window[params.appletReadyScriptName] = this.appletReadyScript;
    window[params.recordStateChangedScriptName] = this.recordStateChanged;

    this.RECORD_BUTTON_SELECTOR = params.recordButtonId || "#id_record_button";
    this.CANCEL_BUTTON_SELECTOR = params.cancelButtonId || "#id_cancel_button";
    
    // ATTRIBUTES

    this.block = $(selector);
    this.urls = urls;
    this.uploadedCount = 0;
    this.uploadedTime = 0.0;
    this.minLengthToUpload = params.minLengthToUpload || 1.5;
    this.appletName = params.appletName || "ListenUpRecorder";

    console.log('Applet name:', this.appletName);

    // BUTTONS CALLBACKS
    this.recordButtonClicked = function () {
        if (this_.applet.isRecording()) {
            this_.event("pause");
        } else {
            this_.event("record");
        }
    };

    this.cancelButtonClicked = function () {
        this_.event("cancel");
    };

    this.block.find(this.RECORD_BUTTON_SELECTOR).click(this.recordButtonClicked);
    this.block.find(this.CANCEL_BUTTON_SELECTOR).click(this.cancelButtonClicked);

    // Main condition to check if we can send data
    this.canSendToVerification = function () {
        return this.applet.isPlayable() && this.applet.getMaxPlayableTime() > this.minLengthToUpload;
    }

    this.record_recording_to_paused  = function () {
        this.event("paused");
    };

    // Helper functions
    this.return_back = function (args) {
        window.location = this.urls.fallbackURL;
    };

    this.setButtonEnabled = function(selector, is_enabled) {
        if (is_enabled) {
            this.block.find(selector).removeAttr("disabled");
        } else {
            this.block.find(selector).attr("disabled", "true");
        }
    };

    this.maskButtons = function(record_mask, cancel_mask) {
        this.setButtonEnabled(this.RECORD_BUTTON_SELECTOR, record_mask);
        this.setButtonEnabled(this.CANCEL_BUTTON_SELECTOR, cancel_mask);
    };

    this.getContent = function() {
        return this.block.find(".voice_auth_content");
    };

    this.clearContent = function() {
        this.getContent().html('');
    };

    this.pasteNote = function (note) {
        this.getContent().html('<span class="note">' + note + '</span>');
    };

    this.pasteError = function (note) {
        this.getContent().html('<span class="errornote">' + note + '</span>');
    };

    this.setLoading = function(message) {
        currentUploadingTime = this.applet.getMaxPlayableTime();
        this.getContent().html(
            '<img src="/media/img/loading.gif" id="id_loading_img" /><span class="loadingMessage">' + message + '</span>'
        );
    };

    this.sessionContext = function() {
        return this.block.find("form").serializeArray();
    };

    this.sessionId = function() {
        return this.block.find("form input[name=session_id]").val();
    };

    if (!defer_creation) {
        this.event("created");
    }
};

// Default state transitions
BaseVoiceBlock.method('to_initial', function (args) {
    this.state = "initial";
    this.pasteNote("Нажмите кнопку &laquo;Запись&raquo;, произнесите ключевую фразу, и нажмите на кнопку &laquo;Стоп&raquo;.");
    this.maskButtons(true, true);
});

BaseVoiceBlock.method('to_recording', function (args) {
    this.state = "recording";
    this.setLoading("Идёт запись..");
    this.block.find(this.RECORD_BUTTON_SELECTOR).val("Стоп");
    this.maskButtons(true, false);
    this.applet.record();
});

BaseVoiceBlock.method('to_pausing', function (args) {
    this.state = "pausing";
    this.applet.pauseAudio();
});

BaseVoiceBlock.method('to_uploading', function (args) {
    this.state = "uploading";
    this.maskButtons(false, false);
    this.setLoading("Запись отправляется на сервер..");
    this.applet.stopAudio();

    this.applet.addNameValuePair("session_id", this.sessionId());
    this.applet.sendRecordedMessage();
});

BaseVoiceBlock.method('to_paused', function (args) {
    this.state = "paused";
    this.block.find(this.RECORD_BUTTON_SELECTOR).val("Запись");
    console.log("Recorded utterance, going to send..");
    if (this.canSendToVerification()) {
        this.event("ready_to_upload");
    } else {
        this.event("too_short_to_upload",
                {recorded_time: this.applet.getMaxPlayableTime()}
        );
    }
});

BaseVoiceBlock.method('to_insufficient_to_upload', function (args) {
    this.state = "insufficient_to_upload";
    this.pasteNote(sprintf('Записан слишком короткий образец (%.2f сек.). Повторите запись ещё раз.',
                args.recorded_time));
    this.maskButtons(true, true);
});

BaseVoiceBlock.method('to_upload_failed', function (args) {
    this.state = "upload_failed";
    this.pasteError("Ошибка при отправке записи на сервер. Попробуйте ещё раз или обратитесь в службу поддержки.");
    this.maskButtons(false, true);
});

BaseVoiceBlock.method("to_upload_completed", function (args) {
    this.state = "upload_completed";
    this.pasteNote("Запись отправлена.");
    this.maskButtons(true, true);
    this.uploadedCount += 1;
    this.uploadedTime += this.currentUploadingTime;
    this.currentUploadingTime = undefined;
});

