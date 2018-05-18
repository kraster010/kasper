function input_history(){
    let history_max = 21;
    let history = new Array();
    let history_pos = 0;

    history[0] = '';


    let back = function(){
        return "back";
    };

    let fwd = function(){
        return "fwd";        
    };

    let add = function(){
        return "add";        
    };

    let end = function(){
        return "end";        
    };

    let scratch = function(){
        return "scratch";        
    };


    return {
        back: back,
        fwd: fwd,
        add: add,
        end: end,
        scratch: scratch
    }
};

export {
    input_history
};