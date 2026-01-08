//
//---   openplot.js: Script containing function to open plot subpages
//---   w. aaron (william.aaron@cfa.harvard.edu)
//---   Last Update: Jan 08, 2026
//

var plotUrl = new URL('Plots', window.location.href);

function openPlot(category) {
    const goto = new URL(`${plotUrl.href}/${category}.html`);
    window.open(goto, category);
}