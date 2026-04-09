/** @odoo-module **/

import { beforeEach, describe, expect, test } from "@odoo/hoot";
import {
    contains,
    mockService,
    mountWithCleanup,
    onRpc,
    patchWithCleanup,
} from "@web/../tests/web_test_helpers";
import { animationFrame } from "@odoo/hoot-mock";
import { defineMailModels } from "@mail/../tests/mail_test_helpers";

import { CopilotSystrayButton } from "@ipai_odoo_copilot/js/copilot_systray";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeFile(name, type, size = 1024) {
    const content = new Uint8Array(size);
    return new File([content], name, { type });
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("CopilotSystrayButton", () => {
    defineMailModels();

    beforeEach(() => {
        patchWithCleanup(odoo, { csrf_token: "dummy" });
        mockService("action", {
            get currentController() {
                return null;
            },
        });
        // Mock the config parameter check in onMounted
        onRpc("ir.config_parameter", "get_param", () => "True");
    });

    test("renders systray button", async () => {
        await mountWithCleanup(CopilotSystrayButton);
        expect(".o_ipai_copilot_systray").toHaveCount(1);
        expect(".o_ipai_copilot_btn").toHaveCount(1);
        expect(".o_ipai_copilot_panel").toHaveCount(0, {
            message: "Panel should be closed initially",
        });
    });

    test("toggle panel open and close", async () => {
        await mountWithCleanup(CopilotSystrayButton);

        await contains(".o_ipai_copilot_btn").click();
        await animationFrame();
        expect(".o_ipai_copilot_panel").toHaveCount(1, {
            message: "Panel should open on click",
        });

        await contains(".o_ipai_copilot_btn").click();
        await animationFrame();
        expect(".o_ipai_copilot_panel").toHaveCount(0, {
            message: "Panel should close on second click",
        });
    });

    test("close panel via close button", async () => {
        await mountWithCleanup(CopilotSystrayButton);

        await contains(".o_ipai_copilot_btn").click();
        await animationFrame();
        expect(".o_ipai_copilot_panel").toHaveCount(1);

        await contains(".o_ipai_copilot_panel .fa-times").click();
        await animationFrame();
        expect(".o_ipai_copilot_panel").toHaveCount(0);
    });

    test("shows empty state when no messages", async () => {
        await mountWithCleanup(CopilotSystrayButton);

        await contains(".o_ipai_copilot_btn").click();
        await animationFrame();
        expect(".o_ipai_copilot_empty").toHaveCount(1, {
            message: "Empty state placeholder should be visible",
        });
    });

    test("paperclip button is visible in input area", async () => {
        await mountWithCleanup(CopilotSystrayButton);

        await contains(".o_ipai_copilot_btn").click();
        await animationFrame();
        expect(".o_ipai_copilot_attach_btn").toHaveCount(1, {
            message: "Paperclip attach button should be present",
        });
        expect(".o_ipai_copilot_attach_btn .fa-paperclip").toHaveCount(1);
    });

    test("hidden file input has correct accept attribute", async () => {
        await mountWithCleanup(CopilotSystrayButton);

        await contains(".o_ipai_copilot_btn").click();
        await animationFrame();
        const fileInput = document.querySelector(
            ".o_ipai_copilot_input input[type='file']"
        );
        expect(Boolean(fileInput)).toBe(true);
        expect(fileInput.hasAttribute("multiple")).toBe(true);
        expect(fileInput.getAttribute("accept")).toInclude("image/png");
        expect(fileInput.getAttribute("accept")).toInclude("application/pdf");
    });

    test("getFileIcon returns correct icons", async () => {
        const comp = await mountWithCleanup(CopilotSystrayButton);

        expect(comp.getFileIcon({ type: "image/png" })).toBe(
            "fa fa-file-image-o"
        );
        expect(comp.getFileIcon({ type: "application/pdf" })).toBe(
            "fa fa-file-pdf-o"
        );
        expect(comp.getFileIcon({ type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" })).toBe(
            "fa fa-file-word-o"
        );
        expect(comp.getFileIcon({ type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" })).toBe(
            "fa fa-file-excel-o"
        );
        expect(comp.getFileIcon({ type: "text/plain" })).toBe(
            "fa fa-file-o"
        );
        expect(comp.getFileIcon(null)).toBe("fa fa-file-o");
    });

    test("attachment chips appear after adding file to state", async () => {
        const comp = await mountWithCleanup(CopilotSystrayButton);

        await contains(".o_ipai_copilot_btn").click();
        await animationFrame();

        // Simulate adding a file to the state directly
        comp.state.attachments.push(makeFile("test.pdf", "application/pdf"));
        await animationFrame();

        expect(".o_ipai_copilot_attachment_chip").toHaveCount(1);
    });

    test("remove attachment chip", async () => {
        const comp = await mountWithCleanup(CopilotSystrayButton);

        await contains(".o_ipai_copilot_btn").click();
        await animationFrame();

        comp.state.attachments.push(makeFile("a.pdf", "application/pdf"));
        comp.state.attachments.push(makeFile("b.png", "image/png"));
        await animationFrame();

        expect(".o_ipai_copilot_attachment_chip").toHaveCount(2);

        // Remove first attachment
        await contains(".o_ipai_copilot_attachment_chip .btn-close").click();
        await animationFrame();
        expect(".o_ipai_copilot_attachment_chip").toHaveCount(1);
    });

    test("rejects files with unsupported MIME type", async () => {
        const comp = await mountWithCleanup(CopilotSystrayButton);

        await contains(".o_ipai_copilot_btn").click();
        await animationFrame();

        // Simulate onFileSelected with unsupported type
        const unsupportedFile = makeFile("script.js", "text/javascript");
        comp.onFileSelected({
            target: {
                files: [unsupportedFile],
                set value(_v) {},
            },
        });
        await animationFrame();

        expect(comp.state.attachments).toHaveLength(0, {
            message: "Unsupported file type should be rejected",
        });
        expect(Boolean(comp.state.error)).toBe(true);
    });

    test("rejects files exceeding MAX_FILE_SIZE", async () => {
        const comp = await mountWithCleanup(CopilotSystrayButton);

        await contains(".o_ipai_copilot_btn").click();
        await animationFrame();

        const oversized = makeFile(
            "huge.pdf",
            "application/pdf",
            51 * 1024 * 1024 // 51 MB
        );
        comp.onFileSelected({
            target: {
                files: [oversized],
                set value(_v) {},
            },
        });
        await animationFrame();

        expect(comp.state.attachments).toHaveLength(0, {
            message: "Oversized file should be rejected",
        });
        expect(comp.state.error).toInclude("too large");
    });

    test("enforces MAX_FILES limit", async () => {
        const comp = await mountWithCleanup(CopilotSystrayButton);

        await contains(".o_ipai_copilot_btn").click();
        await animationFrame();

        // Fill up to max
        for (let i = 0; i < 10; i++) {
            comp.state.attachments.push(
                makeFile(`file${i}.png`, "image/png")
            );
        }

        // Attempt to add one more via onFileSelected
        comp.onFileSelected({
            target: {
                files: [makeFile("extra.png", "image/png")],
                set value(_v) {},
            },
        });
        await animationFrame();

        expect(comp.state.attachments).toHaveLength(10, {
            message: "Should not exceed MAX_FILES=10",
        });
        expect(comp.state.error).toInclude("Maximum");
    });

    test("clear messages resets attachments and errors", async () => {
        const comp = await mountWithCleanup(CopilotSystrayButton);

        await contains(".o_ipai_copilot_btn").click();
        await animationFrame();

        comp.state.messages.push({
            role: "user",
            content: "test",
            timestamp: "12:00",
        });
        comp.state.attachments.push(makeFile("f.pdf", "application/pdf"));
        comp.state.error = "some error";
        await animationFrame();

        await contains(".fa-plus").click();
        await animationFrame();

        expect(comp.state.messages).toHaveLength(0);
        expect(comp.state.attachments).toHaveLength(0);
        expect(comp.state.error).toBe(null);
    });
});
