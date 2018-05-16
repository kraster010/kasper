import Gui from './modules/webclient_gui';

(function(document, window) {

    TG.onReady = function() {
        TG.Gui = new Gui();
        TG.Gui.init();
    };

 $(document).ready(TG.onReady);

}(document, window));