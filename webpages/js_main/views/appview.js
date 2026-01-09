//
//--- vews/appview.js: 
//---       t. isobe (tisobe@cfa.harvard.edu) based on D. Jones script
//---       Last Update: Apr 19, 2018
//

var app = app || {};

app.AppView = Backbone.View.extend({
    
    el: "#dashapp",
    el2: "#comp",

    events:{
        'click .stop-msid' : 'stopRun',         //--- stop continuous listening
        'click .act-msid'  : 'restartRun'       //--- restuart listening the events
    },

//-----------------------
    
    initialize: function() {
        app.MSIDInfoList.fetch();               //--- read msid information

        console.log('Initialized');

        this.listenTo(app.MSIDList, 'blobdone', function(arguments) {
            //console.log('BLOBDONE');
            if (arguments['type'] && arguments['type'] === "SC") {
                this.renderTime(arguments['time']);
            }
        });

        this.listenTo(app.MSIDList, 'modeladded', function(arguments) {
            console.log('TRIGGERED');
            this.addOne(arguments);
        });
    },
//-----------------------

    addOne: function(args) {
        
        var newModel = args['newModel'];
        var thisEl   = args['element'];
        
        var view = new app.MSIDView({'model': newModel, 'el': thisEl});
        $(thisEl).append(view.render().el);
    },

//-----------------------

    renderTime: function(blobTime) {
        //
        //--- re-format the time into yyyy:ddd:hh:mm:ss.sss
        //
        var blobTimeDisp =
            blobTime.substring(0,   4) + ":" +
            blobTime.substring(4,   7) + ":" +
            blobTime.substring(7,   9) + ":" +
            blobTime.substring(9,  11) + ":" +
            blobTime.substring(11, 13) //+ "." +
            //blobTime.substring(13, 16);           //--- removed msec part
     
        $('#blobtime').html(blobTimeDisp);
    },
    
//-----------------------

    stopRun: function(){
        //
        //--- stop listening the event
        //
        this.stopListening(app.MSIDList, 'blobdone');
        this.stopListening(app.MSIDList, 'modeladded');
        console.log('Stopped');
    },
    
//-----------------------

    restartRun: function(){
        //
        //--- restart listening the event
        //

        console.log('Restarted');

        app.MSIDInfoList.fetch();

        this.listenTo(app.MSIDList, 'blobdone', function(arguments) {
            if (arguments['type'] && arguments['type'] === "SC") {
                this.renderTime(arguments['time']);
            }
        });

        this.listenTo(app.MSIDList, 'modeladded', function(arguments) {
            this.addOne(arguments);
        });
    },
});
