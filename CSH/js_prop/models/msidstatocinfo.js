//
//--- models/msidinfo.js: MSID information model
//---       t. isobe (tisobe@cfa.harvard.edu) copied from d. jones script
//---       Last Update: Aug 24, 2017
//

app.MSIDStaticInfo = Backbone.Model.extend({
    
    // Defaults
    defaults: { name: null, value: null},
    
    // ID Attribute     ---- a model's unique identifier
    
         idAttribute: ['name']
});
