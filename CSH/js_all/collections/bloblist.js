//
//--- bloblist.js: collection of blob model (data from occ)
//---       t. isobe (tisobe@cfa.harvard.edu) based on D. Jones scripts
//---       Last Update: Apr 11. 2019
//
var app = app || {};



function zerofill(number, width) {
    //
    //---- filling '0' with leading space 
    //
	width -= number.toString().length;

	if (width > 0) {
		return new Array( width + (/\./.test(number) ? 2 : 1)).join('0') + number;
	}

	return number + "";
}


//--------------------

app.BlobList = Backbone.Collection.extend({
	model: app.Blob,

	// baseURL: '',

	// This function changed as part of the changes to implement binary
	// and circumvent typical JSON processing. It is not clear what I changed
	// that drove this changed. This function used to take just an options argument and
	// worked fine. However, with the other changes I made, initialize was interpreting
	// the options as a model to be added. Docs do suggest two arguments (initial model(s) array
	// and options) which is what I end up with here, and it works as expected when null
	// is passed for the data argument.   (D. Jones)
    //
    // This one is now read a local JSON data file: blob_all.json   (Apr 19, 2018, TI)

//-------------------

	initialize: function(data, options) {


		options || (options = {});
		this.lastTime       = options.lastTime;
		this.baseURL        = options.baseURL;
		this.lastFetchStart = options.lastFetchStart;

		// Start this at NOW so that we won't immediately lapse into slower queries

		this.lastNonEmptyFetchStart = Date.now();
	},

	url: function() {
		if (!this.lastTime) {
			return this.baseURL;
		}

		return this.baseURL + "ts=" + this.lastTime;
	},


//-------------------

	setLastTime: function(lastTime) {

		var that = this;

		// Time comes in as YYYYDOYHHMMSSUUU
		// Need to add one millisecond

		var nextFetchDelay = 0;

		if (lastTime === 0) {
			this.lastTime = null;

		} else {
			if (lastTime != null) {
				// We use the previous last time to

				var lastTimeStr = lastTime.toString();
				var year = Number(lastTimeStr.substring(0, 4));
				var doy  = Number(lastTimeStr.substring(4, 7));
				var hour = Number(lastTimeStr.substring(7, 9));
				var min  = Number(lastTimeStr.substring(9, 11));
				var sec  = Number(lastTimeStr.substring(11, 13));
				var msec = Number(lastTimeStr.substring(13, 16)) + 1;

				var lastTimeAsDate = new Date(year, 0, doy, hour, min, sec, msec);
				var start          = new Date(year, 0, 0);
				var diff           = lastTimeAsDate-start;
				var oneDay         = 1000 * 60 * 60 * 24;
				var newDoy         = Math.floor(diff / oneDay);

				var nextTimeStr = zerofill(lastTimeAsDate.getFullYear(), 4) +
				                  zerofill(newDoy,                       3) +
				                  zerofill(lastTimeAsDate.getHours(),    2) +
				                  zerofill(lastTimeAsDate.getMinutes(),  2) +
				                  zerofill(lastTimeAsDate.getSeconds(),  2) +
				                  zerofill(lastTimeAsDate.getMilliseconds(), 3);

				this.lastTime = nextTimeStr;
			}

			if (this.lastFetchStart) {
				var lastFetchDur = Date.now() - this.lastFetchStart;
				nextFetchDelay   = 256 - lastFetchDur;

				if (nextFetchDelay < 0) {
					nextFetchDelay = 0;
				}
			}

			// If the last non-empty was too long ago: slow down queries

			var lastNonEmptyDur = Date.now() - this.lastNonEmptyFetchStart;

			if (lastNonEmptyDur > 60000) {
				nextFetchDelay += 10000;
			}
		}

//-------------------

		setTimeout(function() {
			that.fetch({error: function(collection, response, options) { 
                console.log("Possible Internal Error"); that.setLastTime(0); } });
		}, nextFetchDelay);
	},


//-------------------

	// the fetch function is totally different from the original one made by D. J.
    // this one just read the local JSON data file (blob_all.json), instead of reading bianry
    // data from occ site (Apr 19, 2018, ti)

	fetch: function() {
		var that = this;

		this.lastFetchStart = Date.now();

        $.getJSON('/mta/CSH/blob_all.json', function(data) {

            var blobs   = [];
            var indices = [];
            var values  = [];
            var names   = [];
            var schecks = [];
            var flags   = [];
            var curBlobTime;

            $.each(data, function(index, dset){
                indices.push(dset.index)
                values.push(dset.value)
                names.push(dset.msid)
                schecks.push(dset.scheck)
                flags.push(dset.f)
                curBlobTime = dset.time
            });
            //
            // save the blob dictionary into blobs array
            //
            blobs.push({time:    curBlobTime,
                        indices: indices,        //--- array
                        values:  values,         //--- array
                        names:   names,          //--- array; this one is now the key of the data
                        schecks: schecks,        //--- status check
                        f:       flags});


		    if (blobs.length > 0) {
			    that.add(blobs);
			    that.lastNonEmptyFetchStart = that.lastFetchStart;
		    } else {
			    // Causes NON-reset of last time
			    that.setLastTime(null);
		    }
        });
	},
});

app.monBlobList = new app.BlobList(null, {'baseURL': "/mta/CSH/blob_all.json"});
app.scBlobList  = new app.BlobList(null, {'baseURL': "/mta/CSH/blob_all.json"});

