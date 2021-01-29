//
//--- models/blobs.js: the model for data from occ database
//---       t. isobe (tisobe@cfa.harvard.edu) copied from d. jones script
//---       Last Update: Aug 24, 2017
//
var app = app || {};

app.Blob = Backbone.Model.extend({

    defaults: {
        time:       null,
        indices:    [],
        values:     [],
        f:          0
    },
    
    id: 'time',
});

