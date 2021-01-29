//
//---   views/msidview.js:
//---       t. isobe (tisobe@cfa.harvard.edu) based on D. Jones script
//---       Last Update: May 15, 2018
//

var app = app || {};

app.MSIDView = Backbone.View.extend({
		
    printfmt: undefined,
    fshort: undefined,

    msidTpl:  _.template( $('#msid-template').html() ),
    msidTpl2: _.template("<td><%= value %></td>"),
	
    initialize: function(options) {
        if(this.el.dataset.descr !== undefined){
            this.descr = this.el.dataset.descr;
        }else{
            this.descr = this.model.get('description');
            var idx    = this.model.get('idx');
            var name   = this.model.get('name');
            var lim    = this.model.get('lim');
        }

        if(this.el.dataset.printfmt !== undefined) {
            this.printfmt = this.el.dataset.printfmt;
        }

        if(this.el.dataset.fshort !== undefined) {
            this.fshort = this.el.dataset.fshort;
        }

        this.listenTo(this.model, 'change', this.render);
    },
	
//------------------    

    render: function() {
        
        var printfmt     = this.printfmt;
        var renderedVal  = chkFormat(this.model.get('value'), printfmt);

        //--- limit display setting

        var limSet = 'NULL';

        //--- list conditions

        if (this.model.get('expState') !== 'NULL' && this.model.get('expState') !== undefined){
            limSet = '<font color=#BA55D3><b>Expected: ' + this.model.get('expState') + '</b></font>';
            limSet = limSet + '<br /> Possible Choices: (' + this.model.get('stateSet') + ')';

        }else if (this.model.get('yLim') !== 'NULL' ){

        //--- neumeric range conditions

            var yLow  = chkFormat(this.model.get('yLow'),  printfmt);
            var yHigh = chkFormat(this.model.get('yHigh'), printfmt);
            var rLow  = chkFormat(this.model.get('rLow'),  printfmt);
            var rHigh = chkFormat(this.model.get('rHigh'), printfmt);

            if(yLow === undefined){
                limSet = this.model.get('stateSet');

            } else {

                //-- can't use css format due to overlib.js does not like it.
                
                limSet = "<font color=#BA55D3>Yellow: "  + yLow + " / " + yHigh + "</font><br />";
                limSet = limSet + " <font color=#FF0000>RED: "  + rLow + " / " + rHigh + "</font>";
            }

        }else {
            limSet = this.model.get('stateSet');
        }

        //--- special cases for s/c configulation page
        
        if (this.fshort == 'y'){
            this.$el.html(this.msidTpl2({ 'value':        renderedVal,
                                          'limit':        limSet,
                                          'description':  this.descr}));

        }else{

            this.$el.html(this.msidTpl({'name':         this.model.get('name'),
                                        'value':        renderedVal,
                                        'limit':        limSet,
                                        'description':  this.descr}));



            //--- computing load bus power and display it ------

            if(this.model.get('name') == 'ELBV'){

                elbPower = computeLBusPower();
                $("td.comp").replaceWith("<td class='comp'>" + elbPower + "</td>");
            }

        }

        //--- cell background color setting

        var useStColor = true;
        var lstatus    = this.model.get('status');
        if (lstatus == 'WARNING'){
            //--- red warning
            this.$el.css('background-color', computeColorDim("#FF4500", this.model.get('limstep')));
            useStColor = false;

        } else if (lstatus == 'CAUTION'){
            //--- yellow warning
            this.$el.css('background-color', computeColorDim("#F0E68C", this.model.get('limstep')));
            useStColor = false;

        } else {
            this.$el.css('background-color', "#98FB98");
        }

        try{
            var lims = this.model.get('lim')
            var wl   = lims['wl']
            var wh   = lims['wh']
            var cl   = lims['cl']
            var ch   = lims['ch']
        
            var val = this.model.get('val')
            if ((val <= wl) || (val >= wh)){
                this.$el.css('background-color', "#FF4500");
            }else if(( val <= cl) || (val >= ch)){
                this.$el.css('background-color', "#F0E68C");
            }
        }
        catch(err){
            var xxx = 'aaa'
        }

        return this;
    },

});


//-----------------------------

var computeLBusPower = function(){
    
    //--- compute EPS Load bus power

    var vtemp1 = app.MSIDList.findWhere({'name': "ELBI_LOW"});
    var vtemp2 = app.MSIDList.findWhere({'name': "ELBV"});

    if( vtemp1 !== undefined && vtemp2 !== undefined){

        var vattr = _.clone(vtemp1.attributes);
        var tmp_elbi_low = vattr['value']

        var vattr = _.clone(vtemp2.attributes);
        var tmp_elbv = vattr['value']
        
        var elbPower = tmp_elbi_low * tmp_elbv;
        elbPower  = chkFormat(elbPower, '%.3f');
    }else{

        elbPower= -999.0;
    }

    return elbPower;
};

//-----------------------------

var computeColorDim = function(color, numSteps) {

    //--- convert the color into rbg format

    var reducFrac = 0.1 * numSteps;
    
    if (reducFrac === 0) {
        return color;
    }
    
    // Break down to RGB

    var usePound = false;
    
    if (color[0] === "#") {
        color = color.slice(1);
        usePound = true;
    }
    
    var num = parseInt(color, 16);
    
    var r = (num >> 16);
    var b = ((num >> 8) & 0x00FF);
    var g = num & 0x0000FF;
    
    r = r + ((255-r) * reducFrac);
    b = b + ((255-b) * reducFrac);
    g = g + ((255-g) * reducFrac);
    
    return (usePound ? "#":"") + (g | (b << 8) | (r << 16)).toString(16);
};

//-----------------------------

var chkFormat = function(curVal, printfmt) {

    //--- adjust display format for the numeric value
    //--- curVal: value to be formatted
    //--- printfmt: format e.g.: %3.4f

    if (curVal === null){
        var renderedVal = "NaN";

    } else {
        var renderedVal = curVal;
        Number.isInteger = Number.isInteger || function(value) {
          return typeof value === 'number' && 
          isFinite(value) && 
          Math.floor(value) === value;
        };

        if (printfmt !== undefined) {
            var arg = curVal;
            if(! isNaN(Number(arg))){
                arg = Number(arg);
                test = arg;
                if(arg < 0.0){
                    test = -1.0 * test;
                }
               
                //--- determine the format based of the value size

                if (Number.isInteger(test)){
                    printfmt = '%1d'
                }else  if (test == 0.0){
                    printfmt = '%.1f'

                }else  if(test >= 0.001 && test < 1.0){
                    printfmt = '%.3f'

                }else if(test >= 1.0 && test < 100){
                    printfmt = '%.2f'

                }else if (test >= 100 && test < 1000){
                    printfmt = '%.1f'

                }else{
                    printfmt = '%.3e'
                }
                renderedVal = sprintf(printfmt, arg);
            }
        }
    }
    return renderedVal;
};


