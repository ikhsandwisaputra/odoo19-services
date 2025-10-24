{
    "name": "AI Services (Demo placeholder)",
    "version": "1.0.0",
    "summary": "Placeholder for premium AI Services module (icon only).",
    "description": "This module provides a visible placeholder and icon for a premium AI Services module. It's intentionally not installable and will raise an informative error during installation. Use this to display the paid module in Odoo Apps.",
    "category": "Extra Tools",
    "author": "Your Company",
    "website": "https://example.com",
    "license": "LGPL-3",
    "depends": [],
    "data": [
        "views/ai_services_placeholder.xml",
    ],
    "images": [
        "static/description/icon.png",
        "static/description/icon.svg",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "pre_init_hook": "prevent_install_hook",
    "assets": {
        "web.assets_backend": [
            "ai_services/static/src/js/ai_services_tile.js",
        ],
    },
}
