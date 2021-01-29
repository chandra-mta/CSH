//
//---   app.js: run all
//---       t. isobe (tisobe@cfa.harvard.edu) copied from d. jones script
//---       Last Update: Sep 07, 2017
//
var app = app || {};

$(function() {
    new app.AppView();

    app.scBlobList.listenTo(app.MSIDInfoList,  'loaded', app.scBlobList.fetch);
    app.monBlobList.listenTo(app.MSIDInfoList, 'loaded', app.monBlobList.fetch);
});
