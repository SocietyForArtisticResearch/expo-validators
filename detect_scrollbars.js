function isScroller(el) {
    var elStyle = window.getComputedStyle(el, null);
    if (elStyle.overflow === 'scroll' ||
        elStyle.overflowX === 'scroll' ||
        elStyle.overflowY === 'scroll') {
        return true;
    }
    if (elStyle.overflow === 'auto' ||
        elStyle.overflowX === 'auto' ||
        elStyle.overflowY === 'auto') {
        if (el.scrollHeight > el.clientHeight) {
            console.log("scroll: ", el.scrollHeight)
            return true;
        }
        if (el.scrollWidth > el.clientWidth) {
            return true;
        }
    }
    return false;
}

var els = document.querySelectorAll('body *');
var scrollableElements = [];
for (var i = 0, el; el = els[i]; i++) {
    if (isScroller(el)) {
        var parent = el.parentNode; 
        var tool = el;
        if (parent.className && parent.className.includes('tool')) {
            var anchor = parent.querySelector('a');
            scrollableElements.push({
                tag: parent.tagName,
                id: anchor ? anchor.id : '',
                classes: parent.className || '',
                scrollHeight: tool.scrollHeight,
                clientHeight: parent.clientHeight,
                scrollWidth: tool.scrollWidth,
                clientWidth: parent.clientWidth
            });
        }
    }
}
return scrollableElements;