
// Defines a header and footer for the PDF document.


var margin_size = '0.74in'

// I tried many ways to get the content to center vertically, including flexbox
// display, and the only method that worked was using table/table-cell display.
var div_styles = 'display: table; width: 100%; height: 100%; padding: 0; margin: 0; font-size: 54%; font-family: sans;'
var p_styles = 'display: table-cell; vertical-align: middle; margin: 0; text-align: center; font-weight: bold'


exports.header = {
  height: margin_size,
  contents: function(pageNum, numPages) {
    return '<div style="' + div_styles + '"><p style="' + p_styles + '">PPO: Definitions and Documentation</p></div>'
  }
}

exports.footer = {
  height: margin_size,
  contents: function(pageNum, numPages) {
    return '<div style="' + div_styles + '"><p style="' + p_styles + '">Page ' + pageNum + ' of ' + numPages + '</p>'
  }
}

