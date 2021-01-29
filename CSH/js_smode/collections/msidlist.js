//
//--- collections/msidlist.js: collection msid model
//---       t. isobe (tisobe@cfa.harvard.edu) based on D. Jones script
//---       Last Update: Apr 23, 2018
//
var app = app || {};

var MSIDList = Backbone.Collection.extend({

	el:      "#dashapp",
	model:   app.MSIDModel,
    hash:    {},
    dephash: {},

//-------------------

    addModels: function() {
        var that = this;

        //--- First: always have CVCMNCTR. (d.jones)   

        var mnfInfo  = app.MSIDInfoList.findWhere({'name': "CVCMNCTR"});
        //console.log(mnfInfo)
        var mnfModel = _.clone(mnfInfo.attributes);

        mnfModel['hidden']     = true;
        mnfModel['prevvalues'] = [];

        var mnfModelAdded      = that.add(mnfModel, {merge:true});
        var mnfIdx             = mnfInfo.get('idx');
        
        that.dephash[mnfIdx]      = {};
        that.dephash[mnfIdx].cid  = [];
        tcid = mnfModelAdded.cid;
        that.dephash[mnfIdx].cid.push(mnfModelAdded.cid);
        that.dephash[mnfIdx].deps = [];

        $('.msid', this.el).each(function () {          //--- find all msid class entries: jquery
                                                        //--- data-msid='xxxx' gives msid: xxxx
            var name = '';
            var deps = [];

            if (this.dataset.msid !== undefined) {      //--- HTMLElement.dataset: javascript
                name = this.dataset.msid;
            }else{
                name = 'na';
            }

            var newModel = {};
            var info     = app.MSIDInfoList.findWhere({'name': name});
                                                        //-- {name: , description:, sc:, lim:, idx:}
            if (info) {
                newModel = _.clone(info.attributes);    //--- create a shallow copy
                newModel['hidden'] = false;             //--- adding a new attribute 'hidden'
            }

            var modelAdded    = that.add(newModel, {merge:true});   //-- bb: collection.add(models, [opt])
            var modelAddedIdx = modelAdded.get('idx');
            var depHashEntry  = that.dephash[modelAddedIdx];

            if (depHashEntry === undefined) {
                that.dephash[modelAddedIdx]      = {};
                that.dephash[modelAddedIdx].cid  = [];
                that.dephash[modelAddedIdx].cid.push(modelAdded.cid);
                that.dephash[modelAddedIdx].deps = [];

            }else{
                var cidArray = that.dephash[modelAddedIdx].cid;
                var cidToKeep = [];

                for (var i=0; i < cidArray.length; i++) {
                    if (that.get(cidArray[i]['hidden'] === true)) { 
                        that.dephash[modelAddedIdx].cid.splice(i, 1);
                        --i;
                    }
                }
            }


            that.trigger('modeladded', {'newModel': modelAdded, 'element': this});

        });

        //that.dephash[mnfIdx].cid.push(mnfModelAdded.cid);
        that.dephash[mnfIdx].deps = [];

        Object.keys(that.dephash).forEach(function(key) {
            that.dephash[key].deps = _.uniq(that.dephash[key].deps);
        });


    },

//-------------------

    updateValues: function(type) {
        
        var lastTime = null;
        var that     = this;
        var bloblist = (type == "SC") ? app.scBlobList : app.monBlobList;

        bloblist.each(function(v, k) {

            var indices = v.get('indices');
            var values  = v.get('values');
            var msids   = v.get('names');           //--- this is new (Apr 19, 2018)
            var updList = [];

            for (var i = 0; i < indices.length; i++){
                var curIdx   = indices[i];
                var mname    = msids[i];
                var newValue = values[i];
                var m        = null;

                if (that.hash.hasOwnProperty(curIdx)) { 

                    //--- check this one is already in the array

                    m = that.get(that.hash[curIdx]);
                }else{

                    //--- add to hash 
                    //--- name is now used to find the data instead of idx (Apr 19, 2018)

                    var result = that.where({name: mname});
                    if (result.length > 0){
                        //if (mname === "3FAMOVE"){
                        //console.log(mname +'<-->' + result[0].cid);
                        //}
                        var m = result[0];
                        that.hash[curIdx] = m.cid;
                    }
                }

                if (m !== null){
                    var mSC = m.get('sc');

                    if ( ( mSC !== null )  && ( newValue < mSC.length ) ) {
                        newValue = mSC[newValue];
                    }

                    //--- keep the last 4 values in 'prevvalues'
                    
                    var curVal = m.get('value');

                    //if (curVal !== null){
                    if (curVal !== null && curVal !== 'NaN' && curVal !== undefined && curVal === '' && curVal !== 999.0){

                        var prevVals = m.get('prevvalues');
                        if (prevVals.length >= 4){
                            prevVals.pop();
                        }
                        prevVals.unshift(curVal);
                        m.set('prevvalues', prevVals);
                    }

                    m.set('value', newValue);

                    var dephashentry = that.dephash[curIdx];
                    if (dephashentry !== undefined) {
                        var deps = that.dephash[curIdx].deps;
                        _.each(deps, function(x){
                            console.log(x);
                            updList.push(x);
                        });
                    }
                    updList.push(curIdx);
                }
            }

            var modUpdateList = [];
            for (var i=0; i < updList.length; i++) {

                if (that.dephash[updList[i]] !== undefined) {
                    var cidList = that.dephash[updList[i]].cid;
                    for (var j=0; j < cidList.length; j++) {
                        modUpdateList.push(that.get(cidList[j]));
                    }
                }
            }

            //--- process all limits

            _.each(modUpdateList.filter(function(m) {
                //console.log(m.get("lim"));
                return (m.get("lim") !== undefined);
            }), function(q) {
                q.procLim();            //--- see Model/msid.js
            });

            lastTime = v.get('time').toString();
            that.trigger('blobdone', {'time': lastTime, 'type': type});
        });

        bloblist.reset();
        bloblist.setLastTime(lastTime);
    }
});

app.MSIDList = new MSIDList();

app.MSIDList.listenTo(app.MSIDInfoList, 'loaded', app.MSIDList.addModels);

app.MSIDList.listenTo(app.scBlobList, 'add', function() {
    app.MSIDList.updateValues("SC");
});

app.MSIDList.listenTo(app.monBlobList, 'add', function() {
    app.MSIDList.updateValues("MON");
});

