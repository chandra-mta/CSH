//
// collections/msidinfolist.js:  Stock collection - use json file, but could add/access one by one
//---       t. isobe (tisobe@cfa.harvard.edu) based on D. Jones script
//---       Last Update: Apr 19, 2018
//

var MSIDInfoList = Backbone.Collection.extend({
    model: app.MSIDInfo,

    fetch: function() {
        var self = this;
        // ideally allow for an overlay within the html rather than
        // in the code. For now just assume we have one here
        // var urls = ['msididx3.json', 'fmain.json'];
        // (Jan 07 2026, WA) Repathed the idx JSON blob to a global variable

        var urls = [idxJsonUrl.pathname];

        var requests = [];
        for (var i=0; i < urls.length; i++) {
            requests.push(
                $.getJSON(urls, function(data) {
                    $.each(data, function(index, o){
                        //console.log(o);
                        self.add(o, {merge: true})
                });
            }));
        }

        // This had to be a function, not just "self.trigger('loaded')" as the argument to then

        $.when.apply(undefined, requests).then(function() {
            self.trigger('loaded');
        });
    }
});

app.MSIDInfoList = new MSIDInfoList();

