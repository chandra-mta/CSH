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

function assignListeners() {
    // Due to this Backbone templater implementation, we actually can't apply event listeners from external libraries.
    // However, using listeners is best practice and helps avoid XSS attacks.
    // Implement this approach in the future once the JS tempalter has been simplified / or new framework is used.
    const buttons = document.querySelectorAll('.plotButton');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            openPlot(this.getAttribute("data-category"));
        });
    });
};