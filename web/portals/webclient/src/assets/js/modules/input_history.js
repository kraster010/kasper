export let input_history = function() {
    
    let history_max = 21;
    let history = new Array();
    let history_pos = 0;

    history[0] = '';



    let back = function(){
        // step backwards in history stack
        this.history_pos = Math.min(++history_pos, history.length - 1);
        return history[history.length - 1 - history_pos];
    };

    let fwd = function(){
        // step forwards in history stack
        this.history_pos = Math.max(--history_pos, 0 );
        return history[history.length - 1 - history_pos];
    };

    let add = function(input){
        // add a new entry to history, don't repeat latest
        if(input && input != history[history.length - 2 ]) {
            if(history.length >= history_max) {
                //kill oldest entry
                history.shift();
            }
            history[history.length - 1 ] = input;
            history[history.length] = '';
        }
        history_pos = 0;
    };

    let end = function(){
        // move to the end of the history stack
        history_pos = 0;
        return history[history.length - 1 ];
    };

    let scratch = function(){
        // Put the input into the last history entry (which is normally empty)
        // without making the array larger as with add.
        // Allows for in-progress editing to be saved.
        history[history.length - 1 ] = input;
    };


    return {
        back: back,
        fwd: fwd,
        add: add,
        end: end,
        scratch: scratch
    }
}();


