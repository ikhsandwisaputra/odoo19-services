odoo.define('ai_services.tile_buttons', function (require) {
    'use strict';

    var core = require('web.core');
    require('web.dom_ready');

    var MODULE_TITLE = 'AI Services (Demo placeholder)';
    var LEARN_MORE_URL = 'https://example.com/ai-services/docs';
    var UPGRADE_URL = 'https://example.com/ai-services/upgrade';

    function replaceButtonsForNode(node) {
        // try to find action container inside the tile
        var actionContainers = node.querySelectorAll('.o_app_actions, .o_app_actions_div, .o_app_card_buttons, .oe_app_icon');
        var container = actionContainers.length && actionContainers[0] ? actionContainers[0] : null;
        if (!container) {
            // fallback: append to tile footer or node itself
            container = document.createElement('div');
            container.className = 'o_app_actions_custom';
            node.appendChild(container);
        }

        // Clear existing children in the container
        while (container.firstChild) container.removeChild(container.firstChild);

        // Create Learn More button
        var aLearn = document.createElement('a');
        aLearn.href = LEARN_MORE_URL;
        aLearn.target = '_blank';
        aLearn.className = 'btn btn-sm btn-secondary';
        aLearn.textContent = 'Learn More';
        container.appendChild(aLearn);

        // Spacer
        var spacer = document.createTextNode(' ');
        container.appendChild(spacer);

        // Create Upgrade button
        var aUpgrade = document.createElement('a');
        aUpgrade.href = UPGRADE_URL;
        aUpgrade.target = '_blank';
        aUpgrade.className = 'btn btn-sm btn-primary';
        aUpgrade.textContent = 'Upgrade';
        container.appendChild(aUpgrade);
    }

    function scanAndReplace() {
        // Find any element that contains the module title text
        var candidates = Array.prototype.slice.call(document.querySelectorAll('.o_app_card, .o_app, .oe_app'));
        candidates.forEach(function (el) {
            if (el.textContent && el.textContent.indexOf(MODULE_TITLE) !== -1) {
                replaceButtonsForNode(el);
            }
        });
    }

    // initial scan
    scanAndReplace();

    // watch for dynamic changes (Apps list loads asynchronously)
    var observer = new MutationObserver(function () {
        scanAndReplace();
    });
    observer.observe(document.body, { childList: true, subtree: true });
});
