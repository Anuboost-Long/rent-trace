from html import escape

ACCENT = "#2F5BEA"
INK = "#14171F"
MUTED = "#5B6270"
PAGE = "#F4F5F7"
LINE = "#E4E6EB"
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"


def _paragraph(text):
    return f'<p style="margin:0 0 16px;font-size:16px;line-height:24px;color:{INK};">{escape(text)}</p>'


def _button(label, url):
    return (
        f'<table role="presentation" cellpadding="0" cellspacing="0" style="margin:8px 0 24px;"><tr>'
        f'<td bgcolor="{ACCENT}" style="border-radius:8px;">'
        f'<a href="{escape(url)}" style="display:inline-block;padding:14px 28px;font-size:16px;'
        f'font-weight:600;color:#ffffff;text-decoration:none;">{escape(label)}</a>'
        f"</td></tr></table>"
        f'<p style="margin:0 0 24px;font-size:13px;line-height:20px;color:{MUTED};">'
        f"Button not working? Copy this link into your browser:<br>"
        f'<a href="{escape(url)}" style="color:{ACCENT};word-break:break-all;">{escape(url)}</a></p>'
    )


def render(heading, paragraphs, button=None, footnote=""):
    body = "".join(_paragraph(text) for text in paragraphs)
    action = _button(*button) if button else ""
    note = (
        f'<p style="margin:0;font-size:13px;line-height:20px;color:{MUTED};">{escape(footnote)}</p>'
        if footnote
        else ""
    )
    return (
        f'<!doctype html><html><body style="margin:0;padding:0;background:{PAGE};">'
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" bgcolor="{PAGE}">'
        f'<tr><td align="center" style="padding:32px 16px;font-family:{FONT};">'
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
        f'style="max-width:480px;">'
        f'<tr><td style="padding:0 0 16px;font-size:20px;font-weight:700;color:{INK};">'
        f'Rent<span style="color:{ACCENT};">Trace</span></td></tr>'
        f'<tr><td bgcolor="#ffffff" style="padding:32px;border:1px solid {LINE};border-radius:12px;">'
        f'<h1 style="margin:0 0 20px;font-size:22px;line-height:28px;color:{INK};">{escape(heading)}</h1>'
        f"{body}{action}{note}"
        f"</td></tr>"
        f'<tr><td style="padding:16px 0 0;font-size:12px;line-height:18px;color:{MUTED};">'
        f"You're receiving this because of activity on your RentTrace account.</td></tr>"
        f"</table></td></tr></table></body></html>"
    )
