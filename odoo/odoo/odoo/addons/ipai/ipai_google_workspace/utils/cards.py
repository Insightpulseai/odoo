# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""Card Service v1 JSON helper functions.

Pure-Python helpers that return plain dicts — no external dependencies.
Reference: https://developers.google.com/workspace/add-ons/reference/rpc/google.apps.card.v1
"""


def card(header=None, sections=None):
    """Build a top-level card dict."""
    c = {}
    if header:
        c["header"] = header
    if sections:
        c["sections"] = sections
    return c


def card_header(title, subtitle=None, image_url=None):
    """Build a CardHeader dict."""
    h = {"title": title}
    if subtitle:
        h["subtitle"] = subtitle
    if image_url:
        h["imageUrl"] = image_url
        h["imageType"] = "CIRCLE"
    return h


def card_section(header=None, widgets=None, collapsible=False):
    """Build a CardSection dict."""
    s = {}
    if header:
        s["header"] = header
    if widgets:
        s["widgets"] = widgets
    if collapsible:
        s["collapsible"] = True
        s["uncollapsibleWidgetsCount"] = 1
    return s


def text_paragraph(text):
    """Build a TextParagraph widget."""
    return {"textParagraph": {"text": text}}


def decorated_text(top_label, text, bottom_label=None, icon=None, on_click=None):
    """Build a DecoratedText widget."""
    dt = {"topLabel": top_label, "text": text}
    if bottom_label:
        dt["bottomLabel"] = bottom_label
    if icon:
        dt["startIcon"] = {"knownIcon": icon}
    if on_click:
        dt["onClick"] = on_click
    return {"decoratedText": dt}


def text_button(text, action_name, parameters=None):
    """Build a TextButton inside a ButtonList widget."""
    action = {"function": action_name}
    if parameters:
        action["parameters"] = [
            {"key": k, "value": v} for k, v in parameters.items()
        ]
    return {
        "buttonList": {
            "buttons": [
                {
                    "text": text,
                    "onClick": {"action": action},
                }
            ]
        }
    }


def divider():
    """Build a Divider widget."""
    return {"divider": {}}


def render_action_response(cards):
    """Wrap card(s) in the renderActions response envelope."""
    return {
        "renderActions": {
            "action": {
                "navigations": [{"pushCard": c} for c in cards]
            }
        }
    }


def render_cards(cards):
    """Wrap card(s) in the top-level response envelope for triggers."""
    return {"action": {"navigations": [{"pushCard": c} for c in cards]}}
