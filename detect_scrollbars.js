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
        if (parent.className && parent.className.includes('tool')) {
            var anchor = parent.querySelector('a');
            scrollableElements.push({
                tag: parent.tagName,
                id: anchor ? anchor.id : '',
                classes: parent.className || '',
                scrollHeight: parent.scrollHeight,
                clientHeight: parent.clientHeight,
                scrollWidth: parent.scrollWidth,
                clientWidth: parent.clientWidth
            });
        }
    }
}
return scrollableElements;