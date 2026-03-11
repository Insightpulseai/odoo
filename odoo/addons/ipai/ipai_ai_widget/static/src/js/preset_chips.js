/** @odoo-module **/
/**
 * PresetChips — OWL component for preset action pills.
 *
 * Renders clickable pill buttons for each AI preset (Summarize, Improve, etc).
 * Presets requiring text selection are disabled when no text is selected.
 *
 * Props:
 *   presets(Array)         — [{ key, label, icon, requires_selection, output_mode }]
 *   hasSelection(Boolean)  — whether the composer has selected text
 *   onPresetSelected(Function) — callback when a preset is clicked
 */

import { Component } from "@odoo/owl";

export class PresetChips extends Component {
    static template = "ipai_ai_widget.PresetChips";
    static props = {
        presets: { type: Array },
        hasSelection: { type: Boolean, optional: true },
        onPresetSelected: { type: Function },
    };

    onSelect(preset) {
        if (preset.requires_selection && !this.props.hasSelection) {
            return;
        }
        this.props.onPresetSelected(preset);
    }
}
