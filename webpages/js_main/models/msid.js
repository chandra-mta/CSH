//
//--- modeles/msid.js: MSID model  
//---       t. isobe (tisobe@cfa.harvard.edu) copied from d. jones script
//---       Last Update: Aug 29, 2017
//
var app = app || {};

app.MSIDModel = Backbone.Model.extend({

	defaults: {
		name:           null,
		id:             null,
		idx:            null,           //--- from msididx.json: gives name, idx, and description
		value:          null,
		prevvalues:     [],
		description:    'NO DESCRIPTION',
		sc:             null,
		printfmt:       null,
        fshort:         null,           //--- indicator of different print format
		lim:            null,
		status:         null,
		limstep:        0,
		hidden:         false,
		calcFn:         null,
		depModelList:   []
	},

//--- read limits

    procLim: function() {

        //--- if no value, stop the limit checking

        if (this.get('value') === null) {
            return;
        }

        //--- limit format: [{"set":{"wl":3.41,"cl":3.71,"ch":48.46,"wh":53.88}}]

        var curLim = this.get('lim');
        this.set('stateSet', this.get('sc'));

        if (!curLim) {
            return this;
        }

        var useSet = null;

        for (var i = 0; i < curLim.length; i++){
            var curSet = curLim[i];

            //--- check whether this limit has "switch" e.g.: {"switch":{"EB1K5":"OFF"}

            var curSwitch = curSet['switch'];
            if (!curSwitch){
                useSet = curSet['set'];
                break;
            }else{
               
                //--- if there are 'set', find which one is used
                
                var swMSIDList = Object.getOwnPropertyNames(curSwitch);

                for(var j = 0; j < swMSIDList.length; j++){
                    var swMSID   = swMSIDList[j];
                    var foundSW  = app.MSIDList.findWhere({'name' : swMSID});
                    var foundVal = '';
                    if (foundSW !== undefined) {
                        var foundVal = foundSW.get('value');
                    }

                    if (foundVal === '' || foundVal === curSwitch[swMSID]){
                        useSet = curSet['set'];
                        break;
                    }
                }
            }

            if (useSet !== null){
                break;
            }
        }

        if (useSet === null){
            this.set('status',   'NULL');
            this.set('expState', 'NULL');
            this.set('yLow',     'NULL');  
            this.set('yHigh',    'NULL');  
            this.set('rLow',     'NULL');  
            this.set('rHigh',    'NULL');  
        } else {
            
            this.set('expState', 'NULL');
            this.set('yLow',     'NULL');  
            this.set('yHigh',    'NULL');  
            this.set('rLow',     'NULL');  
            this.set('rHigh',    'NULL');  

            //--- evaluate the set
           
            var viol = "";
            if (useSet['es']) {
                // can be a list of expected status

                var expStateStr = useSet['es'];
                var expStates   = expStateStr.split(",");

                var curVal      = this.get('value');
                var stateOK     = false;

                for (var i = 0; i < expStates.length; i++){
                    if (curVal === expStates[i]){
                        stateOK = true;
                        break;
                    }
                }

                if (stateOK === false) {
                    viol = 'CAUTION';
                }

                this.set('expState', expStateStr);

            } else if (useSet['cl']) {
                var cautLow  = useSet['cl'];
                var cautHigh = useSet['ch'];
                var warnLow  = useSet['wl'];
                var warnHigh = useSet['wh'];

                var curVal   = this.get('value');

                if(curVal < warnLow || curVal > warnHigh) {
                    viol = 'WARNING';

                }else if (curVal < cautLow || curVal > cautHigh) {
                    viol = 'CAUTION';
                }

                this.set('yLow',  cautLow);
                this.set('yHigh', cautHigh);
                this.set('rLow',  warnLow);
                this.set('rHigh', warnHigh);

            } else if (useSet['mech']) {
                var mech     = useSet['mech'];
                var curVal   = this.get('value');
                var prevVals = this.get('revvalues');

                if (mech === 'INCR') {
                    //--- make sure the current and prior values match
                    var prevVal  = prevVals[0];
                    /*
                    if (curVal < prevVal){
                        console.log(curVal + " " + prevVal);
                        viol = 'CAUTION';
                    }
                    */

                }else if (mech === 'TOGGLE'){
                    var hasViol = 1;
                    if(curVal != prevVals[0]) {
                        hasViol = 0;
                    }else {
                        for (var i = 1; i < prevVals.length; i++){
                            if (prevVals[i] != prevVals[i-1]) {
                                hasViol = 0;
                                break;
                            }
                        }
                    }

                    if (hasViol === 1){
                        viol = 'CAUTION';
                    }
                }
            }

            if (viol === 'WARNING'){
                this.set('status', 'WARNING');
                this.set('limstep', 0);

            } else if (viol === 'CAUTION'){
                this.set('status', 'CAUTION');
                this.set('limstep', 0);

            }else {
                if (this.get('status') !== 'NULL') {
                    var curStep = this.get('limstep');

                    if (curStep === 5){
                        this.set('status', 'NULL');
                        this.set('limstep', 0);

                    } else {
                        this.set('limstep', curStep + 1);
                    }
                }
            }
        }
    },

                
	// ID Attribute	    ---- a model's unique identifier
    
	idAttribute: ['name']
});
