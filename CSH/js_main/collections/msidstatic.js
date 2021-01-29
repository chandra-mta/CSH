//
// collections/msidinfolist.js:  Stock collection - use json file, but could add/access one by one
//---       t. isobe (tisobe@cfa.harvard.edu) based on D. Jones script
//---       Last Update: Apr 24, 2018
//

var MSIDStaticList = Backbone.Collection.extend({
    model: app.MSIDStaticInfo,

    fetch: function() {
        var self = this;

        var self.msidstatic = {}
        var urls = ['/mta/CSH/blob_main.json'];


        var requests = [];
        for (var i=0; i < urls.length; i++) {
            requests.push($.ajax({url: urls[i],
                success: function(data) {
                    $.getJSON( "/mta/CSH/blob_main.json", function( data ) {
                         $.each( data, function( msid, value ) {
                          console.log( value);
                          self.msidstatic[msid] = value;
                    });
                }
            }));
        }

        // This had to be a function, not just "self.trigger('loaded')" as the argument to then

        $.when.apply(undefined, requests).then(function() {
            self.trigger('loaded');
        });
    }
});

app.MSIDStaticList = new MSIDStaticList();

