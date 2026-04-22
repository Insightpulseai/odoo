# -*- coding: utf-8 -*-
{
    "name": "Pulser Chat Shell",
    "version": "18.0.1.0.0",
    "summary": "Thin Owl systray shell for the external Pulser runtime",
    "category": "Productivity",
    "license": "LGPL-3",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "depends": ["base", "web"],
    "data": [
        "data/ir_config_parameter.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_pulser_chat/static/src/js/systray/pulser_systray.js",
            "ipai_pulser_chat/static/src/js/chat/pulser_chat_panel.js",
            "ipai_pulser_chat/static/src/xml/pulser_systray.xml",
            "ipai_pulser_chat/static/src/xml/chat/pulser_chat_panel.xml",
            "ipai_pulser_chat/static/src/scss/pulser_chat.scss",
        ],
    },
    "installable": True,
    "application": False,
}
