import 'evennia';
import {input_history} from 'modules/input_history';

export default class TgGui {

    constructor() {

        this.isConnected = false;
        this.options = {
            debug: true,
        };

        this.notification = {
            unread: 0,
            originalTitle: document.title,
            focused: true,
            favico: null
        };
    }

    init() {
        let _ = this;
        // Event when client finishes loading
        // if ("Notification" in window) {
        //     Notification.requestPermission();
        // }
        _.checkOptions();
        _.initHandshake();
        _.addDOMEvents();
        
    }

    checkOptions() {
        let _ = this;

        // DEBUG STATUS
        if(_.options.debug) {
            $('body').append('<div id="debug"/>');
            console.log("%c Attenzione, i LOG client sono attivi.", 'background: red; color: white');
        }
    }

    initHandshake() {

        let _ = this;
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

    // Ask the user if he wants to reconnect
    reconnect() {
        return false;
    }
    //Performing connection to server via auto or manual request.
    connectToServer() {
        Evennia.connect();
        return;
    }

    // Handle text coming from the server
    onText(args, kwargs) {

        console.log('onText');
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

            _.onNewLine(args[0], null);

        } else {
            console.log('TODO: openPopup(renderto, args[0])')
            // openPopup(renderto, args[0]);
        }
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
    
    // Silences events we don't do anything with.
    onSilence(cmdname, args, kwargs) {}

    // New line insert event (coming from user or server).
    onNewLine(text, originator) {
        console.log('onNewLine');
        let _ = this;
        // Changes unfocused browser tab title to number of unread messages
        // unread++;
        // favico.badge(unread);
        // document.title = "(" + unread + ") " + originalTitle;
        // if (!_.notification.focused) {
            // Changes unfocused browser tab title to number of unread messages
            // _.notification.unread++;
            //   favico.badge(unread);
            // document.title = "(" + unread + ") " + originalTitle;
            // if ("Notification" in window) {
            //     if (("notification_popup" in options) && (options["notification_popup"])) {
            //         Notification.requestPermission().then(function (result) {
            //             console.log('TODO Here');
            //             //     if(result === "granted") {
            //             //     var title = originalTitle === "" ? "Evennia" : originalTitle;
            //             //     var options = {
            //             //         body: text.replace(/(<([^>]+)>)/ig,""),
            //             //         icon: "/static/website/images/evennia_logo.png"
            //             //     }

            //             //     var n = new Notification(title, options);
            //             //     n.onclick = function(e) {
            //             //         e.preventDefault();
            //             //          window.focus();
            //             //          this.close();
            //             //     }
            //             //   }
            //         });
            //     }
            //     if (("notification_sound" in options) && (options["notification_sound"])) {
            //         console.log('TODO Here (audio/sound?)');

            //         // var audio = new Audio("/static/webclient/media/notification.wav");
            //         // audio.play();
            //     }
            // }
        // }
    }

    // Grab text from inputline and send to Server
    doSendText() {

        let _ = this;       

        if(!Evennia.isConnected()) {
            if(reconnect()) {
                //Making a connection if the user does not have one.
                _.onText(['Riconnessione in corso..."'], {cls: "sys"});
                _.connectToServer();

            };
            return ;
        };

        let inputfield = $('#inputfield');
        let outtext = inputfield.val();
        let lines = outtext.trim().replace(/[\r]+/,"\n").replace(/[\n]+/, "\n").split("\n");

        for(var i = 0; i < lines.length; i++) {
            let line = lines[i].trim();
            if(line.length > 7 && line.substr(0,7) == '##send') {
                // send a specific oob instruction ["cmdname",[args],{kwargs}]
                line = line.slice(7);
                let cmdarr = JSON.parse(line);
                let cmdname = cmdarr[0];
                let args = cmdarr[1];
                let kwargs = cmdarr[2];
                
                console.log(cmdarr);
                log(cmdname, args, kwargs);
                Evennia.msg(cmdname, args, kwargs);
            }
            else {
                input_history.add(line);
                inputfield.val('');
                Evennia.msg("text", [line], {});
            }
        }

    }

    // doOpenOptions() {}


    onKeyPress(event) {
        console.log('onKeyPress');        
    }
    
    // catch all keyboard input, handle special chars
    onKeyDown(event) {

        console.log('onKeyDown');
        let _ = this;
        let code = event.which;
        let history_entry = null;
        let inputfield = $('#inputfield');

        inputfield.focus();
        // enter key sends text
        if (code === 13 ) {
            _.doSendText();
            event.preventDefault();
        }
        else if (inputfield[0].selectionStart == inputfield.val().length) {
            // Only process up/down arrow if cursor is at the end of the line.    
            if(code === 30) {

            }
            else if (code === 40) {
                history_entry = input_history.fwd();
            }
        }
        // escape key
        if (code === 27 ) {}
        
    }
    
    addDOMEvents() {
        let _ = this;

        // Pressing the send button
        $("#inputsend").on("click", _.doSendText.bind(_));
         // Event when any key is pressed
        $(document).keydown(_.onKeyDown.bind(_));            
    }

    // Appends any kind of message inside Debug Output box
    clog(msg) {
        let _ = this;
        if (msg) {
            $('#debug').append('DEBUG MSG: ' + msg);
        }
    }

}