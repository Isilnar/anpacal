// ---------------------------------------------------------------------------
// CSRF helpers
// ---------------------------------------------------------------------------

/**
 * Read the CSRF token from the <meta name="csrf-token"> tag set by layout.html.
 * Use this to protect dynamically-created forms and fetch() calls.
 */
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

/**
 * Return a hidden <input> element with the current CSRF token.
 * Use when building forms dynamically in JS.
 */
function csrfInput() {
    let input = document.createElement('input');
    input.setAttribute('type', 'hidden');
    input.setAttribute('name', 'csrf_token');
    input.setAttribute('value', getCsrfToken());
    return input;
}

/**
 * Intercept all fetch() calls to same-origin URLs and inject the CSRF token
 * as X-CSRFToken header automatically — no need to update each fetch() call.
 */
(function patchFetchWithCsrf() {
    const _fetch = window.fetch;
    window.fetch = function (url, options) {
        options = options || {};
        const method = (options.method || 'GET').toUpperCase();
        if (method !== 'GET' && method !== 'HEAD') {
            const isSameOrigin = !url.startsWith('http') || url.startsWith(window.location.origin);
            if (isSameOrigin) {
                options.headers = options.headers || {};
                options.headers['X-CSRFToken'] = getCsrfToken();
            }
        }
        return _fetch(url, options);
    };
})();

// ---------------------------------------------------------------------------
// DOM helpers
// ---------------------------------------------------------------------------

function insertAfter(referenceNode, newNode) {
    referenceNode.parentNode.insertBefore(newNode, null);
}

function removeErrors(){
    let divsToRemove = document.getElementsByClassName("invalid-feedback");
    for (let i = divsToRemove.length-1; i >= 0; i--) {
      divsToRemove[i].remove();
    }
    $(".is-invalid").removeClass("is-invalid");
}

function showError(ele, errorText){
    $("#"+ele).addClass("is-invalid");
    let elError = document.createElement("div");
    elError.setAttribute("class", "invalid-feedback");
    elError.innerHTML = errorText;
    insertAfter(document.getElementById(ele), elError);
}
