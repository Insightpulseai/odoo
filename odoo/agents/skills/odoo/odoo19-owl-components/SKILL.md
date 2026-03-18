---
name: odoo19-owl-components
description: Odoo 19 OWL component library — ActionSwiper, CheckBox, ColorList, Dropdown, Notebook, Pager, SelectMenu, TagsList
metadata:
  author: odoo/documentation
  version: "19.0"
  source: "content/developer/reference/frontend/owl_components.rst, content/developer/reference/frontend/javascript_reference.rst"
  extracted: "2026-02-17"
---

# Odoo 19 OWL Components

## Overview

Odoo's web client is built with **OWL** (Odoo Web Library), a declarative component framework. The framework provides a suite of reusable generic components for common UI patterns.

## OWL Component Structure

Every Odoo OWL component follows the same pattern:

```javascript
import { Component, useState } from "@odoo/owl";

class MyComponent extends Component {
    // Template name follows convention: addon_name.ComponentName
    static template = "myaddon.MyComponent";

    // Declare sub-components used in the template
    static components = { ChildComponent };

    // Props validation (optional but recommended)
    static props = {
        title: { type: String },
        count: { type: Number, optional: true },
    };

    setup() {
        // Initialize state, hooks, services here
        // NEVER use constructor()
        this.state = useState({ value: 1 });
    }

    increment() {
        this.state.value++;
    }
}
```

Template file (`my_component.xml`):

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<templates xml:space="preserve">

<t t-name="myaddon.MyComponent">
    <div t-on-click="increment">
        <t t-esc="state.value"/>
    </div>
</t>

</templates>
```

### Best Practices

1. **Always use `setup()`, never `constructor()`** -- constructors are not overridable via patching.
2. **Template naming**: `addon_name.ComponentName` to prevent collisions.
3. **File organization**: `my_component.js`, `my_component.xml`, `my_component.scss` in the same directory.
4. **Inline templates** (`xml` helper) are only for prototyping. Production templates go in XML files.

```javascript
// CORRECT:
class MyComponent extends Component {
    setup() {
        // initialize here
    }
}

// INCORRECT -- never do this:
class IncorrectComponent extends Component {
    constructor(parent, props) {
        // cannot be patched!
    }
}
```

---

## ActionSwiper

**Location**: `@web/core/action_swiper/action_swiper`

A touch-swipe component that wraps a target element and executes actions when the user swipes horizontally past a threshold.

### Basic Usage

```xml
<ActionSwiper onLeftSwipe="Object" onRightSwipe="Object">
    <SomeElement/>
</ActionSwiper>
```

### Full Example

```xml
<ActionSwiper
    onRightSwipe="{
        action: () => this.deleteItem(),
        icon: 'fa-delete',
        bgColor: 'bg-danger',
    }"
    onLeftSwipe="{
        action: () => this.starItem(),
        icon: 'fa-star',
        bgColor: 'bg-warning',
    }"
>
    <div>
        Swipable item
    </div>
</ActionSwiper>
```

### Props

| Name | Type | Description |
|------|------|-------------|
| `animationOnMove` | `Boolean` | Optional. Translate effect during swipe |
| `animationType` | `String` | Optional. Animation after swipe ends: `"bounce"` or `"forwards"` |
| `onLeftSwipe` | `Object` | If present, enables left swipe |
| `onRightSwipe` | `Object` | If present, enables right swipe |
| `swipeDistanceRatio` | `Number` | Optional. Minimum width ratio to trigger action |

### Swipe Object Shape

```javascript
{
    action: Function,   // Callback executed on complete swipe
    icon: String,       // Icon class (e.g., "fa-check-circle")
    bgColor: String,    // Bootstrap contextual color: "bg-danger", "bg-info",
                        // "bg-secondary", "bg-success", "bg-warning"
}
```

Actions are permuted automatically for RTL languages.

### Extending Existing Components

Use XPath to wrap existing elements in an ActionSwiper:

```xml
<xpath expr="//*[hasclass('o_Message')]" position="after">
    <ActionSwiper
        onRightSwipe="messaging.device.isMobile and messageView.message.isNeedaction ?
            {
                action: () => messageView.message.markAsRead(),
                icon: 'fa-check-circle',
                bgColor: 'bg-success',
            } : undefined"
    />
</xpath>
<xpath expr="//ActionSwiper" position="inside">
    <xpath expr="//*[hasclass('o_Message')]" position="move"/>
</xpath>
```

---

## CheckBox

**Location**: `@web/core/checkbox/checkbox`

A simple checkbox with a linked label (clicking the label toggles the checkbox).

### Usage

```xml
<CheckBox value="boolean" disabled="boolean" t-on-change="onValueChange">
    Some Text
</CheckBox>
```

### Props

| Name | Type | Description |
|------|------|-------------|
| `value` | `boolean` | If true, checkbox is checked |
| `disabled` | `boolean` | If true, checkbox is disabled |

### Example Component

```javascript
import { Component, useState } from "@odoo/owl";
import { CheckBox } from "@web/core/checkbox/checkbox";

class MyForm extends Component {
    static template = "myaddon.MyForm";
    static components = { CheckBox };

    setup() {
        this.state = useState({ agreed: false });
    }

    onAgreeChange(ev) {
        this.state.agreed = ev.target.checked;
    }
}
```

```xml
<t t-name="myaddon.MyForm">
    <CheckBox value="state.agreed" t-on-change="onAgreeChange">
        I agree to the terms and conditions
    </CheckBox>
</t>
```

---

## ColorList

**Location**: `@web/core/colorlist/colorlist`

A predefined color picker. Displays the current color and optionally expands to show all available colors.

### Props

| Name | Type | Description |
|------|------|-------------|
| `canToggle` | `boolean` | Optional. Whether the list expands on click |
| `colors` | `array` | List of colors, each with a unique `id` |
| `forceExpanded` | `boolean` | Optional. Always show expanded list |
| `isExpanded` | `boolean` | Optional. Expanded by default |
| `onColorSelected` | `function` | Callback when color is selected |
| `selectedColor` | `number` | Optional. Currently selected color `id` |

### Color IDs

| ID | Color |
|----|-------|
| 0 | No color |
| 1 | Red |
| 2 | Orange |
| 3 | Yellow |
| 4 | Light blue |
| 5 | Dark purple |
| 6 | Salmon pink |
| 7 | Medium blue |
| 8 | Dark blue |
| 9 | Fuchsia |
| 10 | Green |
| 11 | Purple |

### Example

```javascript
import { Component, useState } from "@odoo/owl";
import { ColorList } from "@web/core/colorlist/colorlist";

class TagEditor extends Component {
    static template = "myaddon.TagEditor";
    static components = { ColorList };

    setup() {
        this.state = useState({ color: 1 });
    }

    onColorSelected(colorId) {
        this.state.color = colorId;
    }
}
```

```xml
<t t-name="myaddon.TagEditor">
    <ColorList
        canToggle="true"
        selectedColor="state.color"
        onColorSelected.bind="onColorSelected"
    />
</t>
```

---

## Dropdown

**Location**: `@web/core/dropdown/dropdown` and `@web/core/dropdown/dropdown_item`

A full-featured dropdown component with extensive capabilities:

- Toggle on click, close on outside click
- Keyboard navigation (arrows, tab, shift+tab, home, end, enter, escape)
- Configurable hotkeys
- Nested sub-dropdowns (auto-open on hover)
- Smart positioning (auto-adjusts direction, handles RTL)
- Sibling dropdowns: when one opens, others toggle on hover
- Repositions on scroll/resize

### Basic Usage

The Dropdown uses two OWL slots:
- **default slot**: the toggle element
- **content slot**: the dropdown menu contents

```xml
<Dropdown>
    <!-- Default slot = toggle -->
    <button class="my-btn" type="button">
        Click me to toggle the dropdown menu!
    </button>

    <!-- Content slot = menu items -->
    <t t-set-slot="content">
        <DropdownItem onSelected="selectItem1">Menu Item 1</DropdownItem>
        <DropdownItem onSelected="selectItem2">Menu Item 2</DropdownItem>
    </t>
</Dropdown>
```

### Dropdown Props

| Name | Type | Description |
|------|------|-------------|
| `menuClass` | `String` | Optional. CSS class for dropdown menu |
| `disabled` | `Boolean` | Optional. Disable dropdown (default: `false`) |
| `items` | `Array` | Optional. Items displayed as DropdownItems |
| `position` | `String` | Optional. Menu position (default: `"bottom-start"`). Valid `usePosition` positions |
| `beforeOpen` | `Function` | Optional. Called before opening (can be async) |
| `onOpened` | `Function` | Optional. Called after opening |
| `onStateChanged` | `Function` | Optional. Called with boolean (isOpen) on open/close |
| `state` | `Object` | Optional. Manual control object (from `useDropdownState`) |
| `manual` | `Boolean` | Optional. Disable default click handlers on toggle |
| `navigationOptions` | `Object` | Optional. Override navigation behavior |
| `holdOnHover` | `Boolean` | Optional. Keep menu position while hovering |
| `menuRef` | `Function` | Optional. Ref for the menu element (from `useChildRef`) |

### DropdownItem Props

| Name | Type | Description |
|------|------|-------------|
| `class` | `String` or `Object` | Optional. CSS class for the item |
| `onSelected` | `Function` | Optional. Callback when item is selected |
| `closingMode` | `"none"` / `"closest"` / `"all"` | Optional. Which parent dropdown closes on select (default: `"all"`) |
| `attrs` | `Object` | Optional. HTML attributes for root element. If `href` is set, renders as `<a>` |

### JavaScript Component

```javascript
import { Component } from "@odoo/owl";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";

class MyMenuComponent extends Component {
    static template = "myaddon.MyMenu";
    static components = { Dropdown, DropdownItem };

    selectItem(item) {
        console.log("Selected:", item);
    }
}
```

```xml
<t t-name="myaddon.MyMenu">
    <Dropdown menuClass="'my-custom-menu'">
        <button class="btn btn-primary">Actions</button>
        <t t-set-slot="content">
            <DropdownItem onSelected="() => this.selectItem('edit')">Edit</DropdownItem>
            <DropdownItem onSelected="() => this.selectItem('delete')">Delete</DropdownItem>
            <DropdownItem
                attrs="{ href: '/some/url' }"
                closingMode="'none'"
            >Open Link</DropdownItem>
        </t>
    </Dropdown>
</t>
```

### Nested Dropdowns

Place `Dropdown` components inside parent dropdown's content slot. Child dropdowns auto-open on hover when parent is open:

```xml
<Dropdown>
    <button>File</button>
    <t t-set-slot="content">
        <DropdownItem onSelected="() => this.onItemSelected('file-save')">Save</DropdownItem>
        <DropdownItem onSelected="() => this.onItemSelected('file-open')">Open</DropdownItem>

        <Dropdown>
            <button>New</button>
            <t t-set-slot="content">
                <DropdownItem onSelected="() => this.onItemSelected('file-new-document')">
                    Document
                </DropdownItem>
                <DropdownItem onSelected="() => this.onItemSelected('file-new-spreadsheet')">
                    Spreadsheet
                </DropdownItem>
            </t>
        </Dropdown>
    </t>
</Dropdown>
```

### Recursive Dropdown Tree

```xml
<t t-name="addon.MainTemplate">
    <div>
        <t t-call="addon.RecursiveDropdown">
            <t t-set="name" t-value="'Main Menu'" />
            <t t-set="items" t-value="state.menuItems" />
        </t>
    </div>
</t>

<t t-name="addon.RecursiveDropdown">
    <Dropdown>
        <button t-esc="name"></button>
        <t t-set-slot="content">
            <t t-foreach="items" t-as="item" t-key="item.id">
                <!-- Leaf node: DropdownItem -->
                <DropdownItem t-if="!item.childrenTree.length"
                    onSelected="() => this.onItemSelected(item)"
                    t-esc="item.name"/>

                <!-- Branch node: recursive Dropdown -->
                <t t-else="" t-call="addon.RecursiveDropdown">
                    <t t-set="name" t-value="item.name" />
                    <t t-set="items" t-value="item.childrenTree" />
                </t>
            </t>
        </t>
    </Dropdown>
</t>
```

### Controlled Dropdown (useDropdownState)

Use `useDropdownState` hook with the `state` prop to programmatically control open/close:

```javascript
import { Component, onMounted } from "@odoo/owl";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { useDropdownState } from "@web/core/dropdown/dropdown_hooks";

class MyComponent extends Component {
    static components = { Dropdown, DropdownItem };
    static template = "myaddon.MyComponent";

    setup() {
        this.dropdown = useDropdownState();

        onMounted(() => {
            this.dropdown.open();  // auto-open on mount
        });
    }

    mightClose() {
        if (Math.random() > 0.5) {
            this.dropdown.close();
        }
    }
}
```

```xml
<t t-name="myaddon.MyComponent">
    <Dropdown state="this.dropdown">
        <div>My Dropdown</div>
        <t t-set-slot="content">
            <button t-on-click="() => this.mightClose()">Close It!</button>
        </t>
    </Dropdown>
</t>
```

The `useDropdownState` return object:
- `open()` -- open the dropdown
- `close()` -- close the dropdown
- `isOpen` -- getter, boolean

Set `manual="true"` to disable default click handlers on the toggle.

### DropdownGroup

**Location**: `@web/core/dropdown/dropdown_group`

Groups multiple Dropdowns so that when one is open, others in the same group auto-open on hover.

```xml
<!-- All dropdowns in same group -->
<DropdownGroup>
    <Dropdown>...</Dropdown>
    <Dropdown>...</Dropdown>
    <Dropdown>...</Dropdown>
</DropdownGroup>

<!-- Named groups for separate grouping -->
<DropdownGroup group="'my-group'">
    <Dropdown>...</Dropdown>
    <Dropdown>...</Dropdown>
</DropdownGroup>

<DropdownGroup group="'my-other-group'">
    <Dropdown>...</Dropdown>
</DropdownGroup>

<!-- This dropdown shares group with the first DropdownGroup -->
<DropdownGroup group="'my-group'">
    <Dropdown>...</Dropdown>
</DropdownGroup>
```

### CSS Note

Dropdown menu elements are rendered inside an overlay container at the bottom of the document (not adjacent to the toggle). Use `menuClass` and `class` props for CSS selectors.

---

## Notebook

**Location**: `@web/core/notebook/notebook`

A tabbed interface for navigating between pages. Tabs can be horizontal (top) or vertical (left).

### Props

| Name | Type | Description |
|------|------|-------------|
| `anchors` | `object` | Optional. Allow anchor navigation to invisible tab content |
| `className` | `string` | Optional. Root element class |
| `defaultPage` | `string` | Optional. Page `id` to show by default |
| `icons` | `array` | Optional. Icons for tabs |
| `orientation` | `string` | Optional. `"horizontal"` or `"vertical"` |
| `onPageUpdate` | `function` | Optional. Callback when page changes |
| `pages` | `array` | Optional. Page definitions (alternative to slots) |

### Slot-based Pages

```xml
<Notebook orientation="'vertical'">
    <t t-set-slot="page_1" title="'Page 1'" isVisible="true">
        <h1>My First Page</h1>
        <p>It's time to build Owl components. Did you read the documentation?</p>
    </t>
    <t t-set-slot="page_2" title="'2nd page'" isVisible="true">
        <p>Wise owl's silent flight.</p>
    </t>
</Notebook>
```

Slot attributes:
- `title`: tab label text
- `isVisible`: whether the tab/page is visible
- `isDisabled`: greys out the tab and makes it inactive

### Props-based Pages

```javascript
import { Component, xml } from "@odoo/owl";
import { Notebook } from "@web/core/notebook/notebook";

class MyTemplateComponent extends Component {
    static template = xml`
        <h1 t-esc="props.title" />
        <p t-esc="props.text" />
    `;
}

class MyComponent extends Component {
    static template = xml`
        <Notebook defaultPage="'page_2'" pages="pages" />
    `;
    static components = { Notebook };

    get pages() {
        return [
            {
                Component: MyTemplateComponent,
                title: "Page 1",
                props: {
                    title: "My First Page",
                    text: "This page is not visible",
                },
            },
            {
                Component: MyTemplateComponent,
                id: "page_2",
                title: "Page 2",
                props: {
                    title: "My second page",
                    text: "You're at the right place!",
                },
            },
        ];
    }
}
```

---

## Pager

**Location**: `@web/core/pager/pager`

A pagination component that displays the current page range and total count (e.g., "9-12 / 20") with Previous/Next navigation buttons.

### Usage

```xml
<Pager offset="0" limit="80" total="50" onUpdate="doSomething" />
```

### Props

| Name | Type | Description |
|------|------|-------------|
| `offset` | `number` | Index of first element (0-based, but pager displays `offset + 1`) |
| `limit` | `number` | Page size. `offset + limit` = index of last element |
| `total` | `number` | Total number of elements |
| `onUpdate` | `function` | Called when page changes (can be async -- pager is locked during execution) |
| `isEditable` | `boolean` | Allow clicking current page to edit (default: `true`) |
| `withAccessKey` | `boolean` | Bind `p` (previous) and `n` (next) access keys (default: `true`) |

### Integration with Control Panel

Use the `usePager` hook to display the pager in the control panel:

```javascript
import { usePager } from "@web/search/pager_hook";

class MyView extends Component {
    setup() {
        this.state = useState({ offset: 0, limit: 80, total: 0 });

        usePager(() => ({
            offset: this.state.offset,
            limit: this.state.limit,
            total: this.state.total,
            onUpdate: async ({ offset, limit }) => {
                this.state.offset = offset;
                this.state.limit = limit;
                await this.loadData();
            },
        }));
    }
}
```

---

## SelectMenu

**Location**: `@web/core/select_menu/select_menu`

A rich dropdown for selecting options with search, grouping, multi-select, and custom templates. Use for complex scenarios where the native `<select>` is insufficient.

### Props

| Name | Type | Description |
|------|------|-------------|
| `choices` | `array` | Optional. List of choices at the top level |
| `class` | `string` | Optional. Root element class |
| `groups` | `array` | Optional. Grouped choices |
| `multiSelect` | `boolean` | Optional. Enable multiple selection (selected values shown as tags) |
| `togglerClass` | `string` | Optional. Class for toggler button |
| `required` | `boolean` | Optional. Prevent deselecting the current value |
| `searchable` | `boolean` | Optional. Show search box |
| `searchPlaceholder` | `string` | Optional. Search box placeholder text |
| `value` | `any` | Optional. Current selected value (Array for multiSelect) |
| `onSelect` | `function` | Optional. Callback when option is chosen |

### Data Shapes

**Choice**:
```javascript
{
    value: "technical_value",  // any type
    label: "Human Readable"    // translated string
}
```

**Group**:
```javascript
{
    label: "Group Label",      // string header for the group
    choices: [/* choice objects */]
}
```

### Basic Example

```javascript
import { Component, xml } from "@odoo/owl";
import { SelectMenu } from "@web/core/select_menu/select_menu";

class MyComponent extends Component {
    static template = xml`
        <SelectMenu
            choices="choices"
            groups="groups"
            value="'value_2'"
        />
    `;
    static components = { SelectMenu };

    get choices() {
        return [
            { value: "value_1", label: "First value" }
        ];
    }

    get groups() {
        return [
            {
                label: "Group A",
                choices: [
                    { value: "value_2", label: "Second value" },
                    { value: "value_3", label: "Third value" },
                ],
            },
            {
                label: "Group B",
                choices: [
                    { value: "value_4", label: "Fourth value" },
                ],
            },
        ];
    }
}
```

### Custom Choice Template

Use slots to customize the toggler and choice appearance:

```xml
<SelectMenu
    choices="choices"
    groups="groups"
    value="'value_2'"
>
    Make a choice!
    <t t-set-slot="choice" t-slot-scope="choice">
        <span class="coolClass" t-esc="choice.data.label" />
    </t>
</SelectMenu>
```

### Bottom Area Slot

Customize the area below the options (e.g., for a "Create" button):

```xml
<SelectMenu choices="choices">
    <span class="select_menu_test">Select something</span>
    <t t-set-slot="bottomArea" t-slot-scope="select">
        <div t-if="select.data.searchValue">
            <button class="btn text-primary"
                t-on-click="() => this.onCreate(select.data.searchValue)">
                Create this article "<i t-esc="select.data.searchValue" />"
            </button>
        </div>
    </t>
</SelectMenu>
```

### Multi-Select

When `multiSelect` is enabled, `value` must be an Array of selected values. Selected items appear as tags in the input.

```xml
<SelectMenu
    choices="choices"
    multiSelect="true"
    value="['value_1', 'value_3']"
    onSelect="onSelect"
/>
```

---

## TagsList

**Location**: `@web/core/tags_list/tags_list`

Displays a list of tags as rounded pills. Tags can be interactive (clickable, deletable) and optionally limited in visible count.

### Props

| Name | Type | Description |
|------|------|-------------|
| `displayBadge` | `boolean` | Optional. Display as badge style |
| `displayText` | `boolean` | Optional. Show text in tag |
| `itemsVisible` | `number` | Optional. Max visible tags (overflow shows "+N" circle) |
| `tags` | `array` | List of tag objects |

### Tag Object Shape

```javascript
{
    id: "unique_id",          // required: unique identifier
    text: "Display Text",    // required: displayed string
    colorIndex: 2,           // optional: color ID (same as ColorList)
    icon: "fa-star",         // optional: icon before text
    img: "/web/image/...",   // optional: circular image before text
    onClick: () => {},       // optional: callback on tag click
    onDelete: () => {},      // optional: callback on delete (shows X button)
}
```

### Example

```javascript
import { Component, xml } from "@odoo/owl";
import { TagsList } from "@web/core/tags_list/tags_list";

class Parent extends Component {
    static template = xml`<TagsList tags="tags" />`;
    static components = { TagsList };

    setup() {
        this.tags = [
            {
                id: "tag1",
                text: "Earth",
                // No onClick/onDelete = plain display
            },
            {
                colorIndex: 1,
                id: "tag2",
                text: "Wind",
                onDelete: () => this.removeTag("tag2"),
                // Has delete button
            },
            {
                colorIndex: 2,
                id: "tag3",
                text: "Fire",
                onClick: () => this.openTag("tag3"),
                onDelete: () => this.removeTag("tag3"),
                // Clickable + deletable
            },
        ];
    }

    removeTag(id) {
        this.tags = this.tags.filter(t => t.id !== id);
    }

    openTag(id) {
        console.log("Open tag:", id);
    }
}
```

### Limited Visibility

```xml
<TagsList tags="tags" itemsVisible="3" />
```

If `tags` has 5 items and `itemsVisible` is 3, it shows 3 tags plus a "+2" indicator.

---

## Component Import Summary

Quick reference for importing all available components:

```javascript
// Core components
import { CheckBox } from "@web/core/checkbox/checkbox";
import { ColorList } from "@web/core/colorlist/colorlist";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { DropdownGroup } from "@web/core/dropdown/dropdown_group";
import { useDropdownState } from "@web/core/dropdown/dropdown_hooks";
import { Notebook } from "@web/core/notebook/notebook";
import { Pager } from "@web/core/pager/pager";
import { SelectMenu } from "@web/core/select_menu/select_menu";
import { TagsList } from "@web/core/tags_list/tags_list";
import { ActionSwiper } from "@web/core/action_swiper/action_swiper";

// Hooks
import { usePager } from "@web/search/pager_hook";
import { useService } from "@web/core/utils/hooks";
import { useAutofocus } from "@web/core/utils/hooks";
import { useBus } from "@web/core/utils/hooks";
import { usePosition } from "@web/core/position_hook";
import { useSpellCheck } from "@web/core/utils/hooks";
```

---

## Registering Components in Templates

Components used in a template must be declared in `static components`:

```javascript
class ParentComponent extends Component {
    static template = "myaddon.ParentComponent";
    static components = {
        Dropdown,
        DropdownItem,
        CheckBox,
        Notebook,
        Pager,
        SelectMenu,
        TagsList,
    };
}
```

All these components are available through Odoo's module system and should be added to the appropriate asset bundle (typically `web.assets_backend`) in your module's `__manifest__.py`.
