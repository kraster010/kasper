import 'evennia';

export default class TgGui {

    constructor() {

        this.isConnected = false;

        this.options = {

        }
        // Notifications
        this.unread = 0;
        this.originalTitle = document.title;
        this.focused = true;
        this.favico = null;
    }

    init() {
        let _ = this;
        // Event when client finishes loading
        if ("Notification" in window) {
            Notification.requestPermission();
        }

        // This is safe to call, it will always only
        // initialize once.
        Evennia.init();
        // register listeners
        Evennia.emitter.on("text", _.onText.bind(this));
        Evennia.emitter.on("prompt", _.onPrompt.bind(this));
        Evennia.emitter.on("default", _.onDefault.bind(this));
        Evennia.emitter.on("connection_close", _.onConnectionClose.bind(this));
        Evennia.emitter.on("logged_in", _.onLoggedIn.bind(this));
        Evennia.emitter.on("webclient_options", _.onGotOptions.bind(this));
        // silence currently unused events
        Evennia.emitter.on("connection_open", _.onSilence.bind(this));
        Evennia.emitter.on("connection_error", _.onSilence.bind(this));
        // set an idle timer to send idle every 3 minutes,
        // to avoid proxy servers timing out on us
        setInterval(function () {
                // Connect to server
                Evennia.msg("text", ["idle"], {});
            },
            60000 * 3
        );
    }

    // Handle text coming from the server

    onText(args, kwargs) {

        let _ = this;
        // append message to previous ones, then scroll so latest is at
        // the bottom. Send 'cls' kwarg to modify the output class.
        let renderto = "main";
        if (kwargs["type"] == "help") {
            if (("helppopup" in options) && (options["helppopup"])) {
                renderto = "#helpdialog";
            }
        }

        if (renderto == "main") {
            let mwin = $("#outputfield");
            let cls = kwargs == null ? 'out' : kwargs['cls'];
            mwin.append("<div class='" + cls + "'>" + args[0] + "</div>");
            mwin.animate({
                scrollTop: document.getElementById("outputfield").scrollHeight
            }, 0);

            onNewLine(args[0], null);
        } else {
            // openPopup(renderto, args[0]);
        }
        _.debug([args, kwargs]);

    }

    onPrompt() {
        console.log('onPrompt')

    }

    onDefault() {
        console.log('onDefault')

    }

    onConnectionClose() {
        console.log('onConnectionClose')

    }

    onLoggedIn() {
        console.log('onLoggedIn')

    }

    onGotOptions() {
        console.log('onGotOptions')

    }

    onSilence(cmdname, args, kwargs) {
        let _ = this;
        _.debug([cmdname, args, kwargs]);
    }

    // onNewLine(text, originator) {
    //     if(!focused) {
    //       // Changes unfocused browser tab title to number of unread messages
    //       unread++;
    //       favico.badge(unread);
    //       document.title = "(" + unread + ") " + originalTitle;
    //       if ("Notification" in window){
    //         if (("notification_popup" in options) && (options["notification_popup"])) {
    //             Notification.requestPermission().then(function(result) {
    //                 if(result === "granted") {
    //                 var title = originalTitle === "" ? "Evennia" : originalTitle;
    //                 var options = {
    //                     body: text.replace(/(<([^>]+)>)/ig,""),
    //                     icon: "/static/website/images/evennia_logo.png"
    //                 }
      
    //                 var n = new Notification(title, options);
    //                 n.onclick = function(e) {
    //                     e.preventDefault();
    //                      window.focus();
    //                      this.close();
    //                 }
    //               }
    //             });
    //         }
    //         if (("notification_sound" in options) && (options["notification_sound"])) {
    //             var audio = new Audio("/static/webclient/media/notification.wav");
    //             audio.play();
    //         }
    //       }
    //     }
    //   }

    // Appends any kind of message inside output box
    debug(msg) {
        console.log('debug');
        let _ = this;
        if (msg) {
            $('.tg-output').append('DEBUG MSG: ' + msg);
        }
    }

}