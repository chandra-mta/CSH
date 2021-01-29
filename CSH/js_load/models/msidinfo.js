//
//--- models/msidinfo.js: MSID information model
//---       t. isobe (tisobe@cfa.harvard.edu) copied from d. jones script
//---       Last Update: Aug 24, 2017
//

app.MSIDInfo = Backbone.Model.extend({
    
    // Defaults
    defaults: { name: null, description: "NO DESCRIPTION", sc: null, lim: null, idx: null},
    
    // ID Attribute
    idAttribute: 'idx'
});
