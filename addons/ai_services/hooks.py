from odoo.exceptions import UserError


def prevent_install_hook(cr):
    """Pre-init hook that prevents installation and shows an explanatory message.

    Odoo will call this before module installation; raising a UserError prevents install
    and shows the message in the UI. We do this because the real module is paid.
    """
    raise UserError(
        "AI Services is a premium, paid module. To install it, please contact your vendor or provide a valid license. This placeholder only provides the icon and listing in Apps."
    )
