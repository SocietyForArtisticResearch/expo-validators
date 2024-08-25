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

function highlightScrollableElements() {
    var els = document.querySelectorAll('body *');
    for (var i = 0, el; el = els[i]; i++) {
        if (isScroller(el)) {
            el.style.border = '2px solid red';
            el.style.backgroundColor = 'rgba(255, 0, 0, 0.2)';
        }
    }
}

highlightScrollableElements();