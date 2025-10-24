AI Services (Placeholder)
=========================

This directory contains a placeholder Odoo module named "AI Services". It's intended to display
an icon and listing in the Odoo Apps menu, but installation is intentionally blocked because
the real module is a paid product.

Behavior:
- The module provides a static description icon at `static/description/icon.svg` so it shows in Apps.
- A `pre_init_hook` raises a UserError to prevent installation and show an explanatory message.

If you are the vendor or have a license, replace `hooks.prevent_install_hook` with a no-op or
remove the hook to allow installation.
