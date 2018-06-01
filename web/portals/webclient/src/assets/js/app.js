/*  TG 2.0 @2018
    Main Client Entry Point */
import 'evennia';
import gui from './modules/webclient_gui';

(function(document, window) {

    TG.onReady = function() {
        TG.gui = new gui();
        TG.gui.init();
    };

 $(document).ready(TG.onReady);

}(document, window));