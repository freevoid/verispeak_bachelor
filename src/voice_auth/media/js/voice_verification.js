function VerificationBlock (selector, params, urls) {

    BaseVoiceBlock.call(this, selector, params, urls, true);

    this.transitionTable["cancel"] = {
        initial: "return_back",
        failed: "return_back",
        error_in_verification: "return_back",
        verification_failed: "return_back",
        insufficient_to_upload: "cancel_verification",
        insufficient_to_verify: "cancel_verification",
        failed_to_upload: "return_back"
    };

    this.transitionTable["verification_started"] = {
        upload_completed: "to_verificating"
    };

    this.transitionTable["error_in_verification"] = {
        verificating: "to_error_in_verification"
    };
    
    this.transitionTable["verification_success"] = {
        verificating: "to_verification_success"
    };

    this.transitionTable["verification_failed"] = {
        verificating: "to_verification_failed"
    };

    this.transitionTable["insufficient_to_verify"] = {
        verificating: "to_insufficient_to_verify"
    };

    this.transitionTable["record"]["insufficient_to_verify"] = "to_recording";


    var this_ = this;
    this.monitorProgress = function() {

        $.get(this_.urls.monitorURL, this_.sessionContext(),
            function (data) {


                var code = data.result;
                if (code == 0) {
                    var state = data.message;
                    if (state == "verification_success") {

                        this_.event("verification_success");
                    } else if (state == "verification_failed") {
                        this_.event("verification_failed");
                    } else if (state == "waiting_for_data") {
                        this_.event("insufficient_to_verify");
                    } else if (state == "failed") {
                        this_.event("error_in_verification", {description: "В процессе аутентификации произошла ошибка"});
                    } else if (state == "canceled") {
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

VerificationBlock.inherits(BaseVoiceBlock);

VerificationBlock.method('to_upload_completed', function (args) {
    this.uber('to_upload_completed');

    var this_ = this;
    $.post(this.urls.confirmURL, this.sessionContext(),
            function (data) {

                if (data.result == 0) { // all ok

                    this_.event("verification_started");
                } else {
                    alert("Необработанная ошибка:", data);
                    // XXX response parsing + client notifying
                }
            }, "json");
});

VerificationBlock.method('cancel_verification', function (args) {

    $.post(cancelURL, getSessionContext(verificationBlock),
            function (data) {
                if (data.result == 0) {
                    window.location = fallbackURL;
                } else {
                    alert(data);
                }
            }, "json");
});

VerificationBlock.method('to_verificating', function (args) {
    this.state = "verificating";
    this.setLoading("Подождите, идёт процесс аутентификации...");
    this.maskButtons(false, false);
    this.monitorProgress();
});

VerificationBlock.method('to_insufficient_to_verify', function (args) {
    this.state = "insufficient_to_verify";
    this.pasteNote('Недостаточно данных для прохождения аутентификации. Пожалуйста, запишите фразу ещё раз.');
    this.maskButtons(true, true);
});


VerificationBlock.method('to_error_in_verification', function (args) {
    this.state = "error_in_verification";
    this.pasteError(args.description +
            '. Попробуйте ещё раз. Если ошибка возникает снова, обратитесь в службу поддержки.');
    this.maskButtons(false, true);
    this.block.find(".voice_auth_inputs").append('<input id="id_retry_button" type="button" onclick="window.location = \'\';" value="Повтор" />')
});

VerificationBlock.method('to_verification_failed', function (args) {
    this.state = "verification_failed";
    this.pasteError("Аутентификация завершена. В доступе отказано. Повторите попытку или воспользуйтесь формой для ввода пароля.");
    this.maskButtons(false, true);
    this.block.find(".voice_auth_inputs").append('<input id="id_retry_button" type="button" onclick="window.location = \'\';" value="Повтор" />')
});

VerificationBlock.method('to_verification_success', function (args) {
    window.location = this.urls.redirectURL;
});

