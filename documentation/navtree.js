// Copyright (C) 2017 Brian J. Stucky
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.


/*
 * Implements a lightweight navigation tree widget that converts a set of
 * nested lists into an interactive tree with expandable/collapsable items.
 */
$(document).ready(function() {
    $('#toc').find('li').each(function(index, domobj) {
        var li = $(domobj);

        if (li.children('ul').length != 0) {
            var link = li.children('a').first();
            var li_container = $('<div class="li_c"></div>');
            var expander = $('<div class="toc_expander collapsed"></div>');
    
            li.prepend(li_container);
            li_container.prepend(link);
            li_container.prepend(expander);
    
            li.children('ul').hide();
    
            var childul = li.children('ul').first();
    
            expander.click(function(evt) {
                expander.toggleClass('expanded');
                expander.toggleClass('collapsed');
                childul.slideToggle(140);
            });
        }
    });

    var expand_all = $('#expand_all').first();
    expand_all.click(function(evt) {
        $('#toc').find('div.toc_expander.collapsed').each(function(index, domobj) {
            var expander = $(domobj);
    
            expander.trigger('click');
        });
    });

    var collapse_all = $('#collapse_all').first();
    collapse_all.click(function(evt) {
        $('#toc').find('div.toc_expander.expanded').each(function(index, domobj) {
            var expander = $(domobj);
    
            expander.trigger('click');
        });
    });
});

