function RegistrationBlock (selector, params, urls) {
    BaseVoiceBlock.call(this, selector, params, urls, true);

    this_ = this;
    this.CONFIRM_BUTTON_SELECTOR = params.confirmButtonId || "#id_confirm_button";
    this.confirmButtonClicked = function () {
        this_.event("confirm");
    };
    $(this.CONFIRM_BUTTON_SELECTOR).click(this.confirmButtonClicked);

    this.transitionTable["cancel"] = {
        initial: "return_back",
        failed: "return_back",
        error_in_verification: "return_back",
        verification_failed: "return_back",
        failed_to_upload: "return_back",
        insufficient_to_upload: "cancel_registration",
        insufficient_to_registrate: "cancel_registration"
    };

    this.transitionTable["record"] = {
        initial: "to_recording",
        insufficient_to_upload: "to_recording",
        upload_completed: "record_another_one"
    };

    this.transitionTable["confirm"] = {
        upload_completed: "to_confirmed"
    };

    this.transitionTable["learning_started"] = {
        confirmed: "to_learning"
    };

    this.transitionTable["error_in_learning"] = {
        verificating: "to_error_in_learning"
    };
    
    this.transitionTable["learning_success"] = {
        verificating: "to_learning_success"
    };

    this.transitionTable["insufficient_to_enroll"] = {
        verificating: "to_insufficient_to_enroll"
    };

    this.maskButtons = function (record_mask, cancel_mask, confirm_mask) {
        this.setButtonEnabled(this.RECORD_BUTTON_SELECTOR, record_mask);
        this.setButtonEnabled(this.CANCEL_BUTTON_SELECTOR, cancel_mask);
        this.setButtonEnabled(this.CONFIRM_BUTTON_SELECTOR, confirm_mask);
    };

    var this_ = this;
    this.monitorProgress = function() {
        console.log("Monitoring..");
        $.get(this_.urls.monitorURL, this_.sessionContext(),
            function (data) {
                console.log("Monitor state:", data.result, data.message);

                var code = data.result;
                if (code == 0) {
                    var state = data.message;
                    if (state == "finished") {
                        console.log("Learning phase completed!")
                        this_.event("learning_success");
                    } else if (state == "waiting_for_data") {
                        this_.event("insufficient_to_enroll");
                    } else if (state == "failed") {
                        this_.event("error_in_verification", {description: "В процессе аутентификации произошла ошибка"});
                    } else if (state == "interrupted") {
                        this_.event("cancel");
                    } else {
                        setTimeout(this_.monitorProgress, this_.monitorDelay);
                    }
                } else {
                    alert("Необработанный ответ:", data);
                }
            }, "json");
    };

    this.event("created");
}

RegistrationBlock.inherits(BaseVoiceBlock);

RegistrationBlock.method('to_upload_completed', function (args) {
    this.uber('to_upload_completed');
    this.maskButtons(true, true, true);
});

RegistrationBlock.method('cancel_registration', function (args) {
    console.log("Canceled");
    this_ = this;
    $.post(this.cancelURL, this.sessionContext(),
            function (data) {
                if (data.result == 0) {
                    window.location = this_.fallbackURL;
                } else {
                    alert(data);
                }
            }, "json");
});

RegistrationBlock.method('to_confirmed', function (args) {
    this_ = this;
    $.post(this.confirmURL, this.sessionContext(),
        function (data) {
            if (data.result == 0) {
                this_.state = "confirmed";
                this_.event("learning_started");
            } else {
                alert(data);
            }
        }, "json");
});

RegistrationBlock.method('to_verificating', function (args) {
    this.state = "verificating";
    this.setLoading("Подождите, идёт процесс верификации..");
    this.maskButtons(false, false);
    this.monitorProgress();
});

RegistrationBlock.method('to_error_in_verification', function (args) {
    this.state = "error_in_verification";
    this.pasteError(args.description +
            '. Попробуйте ещё раз. Если ошибка возникает снова, обратитесь в службу поддержки.');
    this.maskButtons(false, true);
});

RegistrationBlock.method('to_verification_failed', function (args) {
    this.state = "verification_failed";
    this.pasteError("Аутентификация завершилась неудачно. Попробуйте ещё раз или воспользуйтесь обычным способом, нажав кнопку &laquo;Возврат&raquo;.");
    this.maskButtons(false, true);
});

RegistrationBlock.method('to_verification_success', function (args) {
    window.location = this.urls.redirectURL;
});

RegistrationBlock.method('record_another_one', function (args) {
    this.applet.erase();
    this.uber("to_recording");
});

