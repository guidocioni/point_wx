# notes
'''
A floating "share" button, present on every page, that copies the current
address bar URL (already kept in sync with the page + its selected params by
utils/url_sync.py) to the clipboard. No Dash round-trip is needed since the
URL is already correct client-side; everything here is a clientside callback.
'''

# package imports
from dash import html, Output, Input, clientside_callback
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

share_button = dmc.Affix(
    dbc.Button(
        html.I(className="fa-solid fa-share-nodes", id="share-button-icon"),
        id="share-button",
        outline=True,
        color="primary",
        title="Share this page",
    ),
    position={"bottom": 10, "left": 10},
)


'''
Share window.location.href (kept accurate by url_sync.py's replaceState writer).
Always copies the URL to the clipboard first -- the one outcome every browser
supports and the user can rely on -- then, where the browser also exposes the
Web Share API (navigator.share; mobile Safari/Chrome, and apparently some
desktop Chrome builds too), additionally offers the native share sheet as a
bonus for sending straight into Messages/WhatsApp/Mail/etc. Dismissing or not
using that sheet has no bearing on the copy already made. Icon/color feedback
is applied by touching the DOM directly, the same trick footer.py's
back-to-top button already relies on, rather than round-tripping through Dash
props.
'''
clientside_callback(
    """
    async function(n_clicks) {
        if (!n_clicks) {
            return window.dash_clientside.no_update;
        }
        const url = window.location.href;
        const btn = document.getElementById('share-button');
        const icon = document.getElementById('share-button-icon');

        function flash(btnClass, iconClass) {
            if (!btn) {
                return;
            }
            btn.classList.remove('btn-outline-primary');
            btn.classList.add(btnClass);
            if (icon && iconClass) {
                icon.className = iconClass;
            }
            setTimeout(function () {
                btn.classList.remove(btnClass);
                btn.classList.add('btn-outline-primary');
                if (icon) {
                    icon.className = 'fa-solid fa-share-nodes';
                }
            }, 1500);
        }

        let copied = false;
        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(url);
            } else {
                const textarea = document.createElement('textarea');
                textarea.value = url;
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.focus();
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
            }
            copied = true;
        } catch (err) {
            // fall through -- the share sheet below is still worth offering
        }

        if (navigator.share) {
            try {
                await navigator.share({ url: url, title: document.title });
            } catch (err) {
                // dismissing/cancelling the native sheet is not a failure
            }
        }

        flash(copied ? 'btn-success' : 'btn-danger', copied ? 'fa-solid fa-check' : null);
        return window.dash_clientside.no_update;
    }
    """,
    Output("dummy-data", "data", allow_duplicate=True),
    Input("share-button", "n_clicks"),
    prevent_initial_call=True,
)
