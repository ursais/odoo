/** @odoo-module **/

/*
 * Ticket VIT/S04433 - "Pink screen opening SO".
 *
 * Opening certain records (e.g. Sales Orders whose line list uses the
 * section-and-note renderer) raises an uncaught OwlError:
 *
 *     Invalid props for component 'OptionalFieldsDropdown':
 *     'listRendererClass' is missing (should be a string)
 *
 * The `OptionalFieldsDropdown` component (introduced in Odoo 17) declares
 * `listRendererClass` as a *required* String prop, but some render paths -
 * observed with developer/debug mode plus the dark theme, and with customised
 * list renderers - do not forward it. OWL prop validation then throws and blanks
 * the whole form view.
 *
 * The most robust and least intrusive fix is to make `listRendererClass`
 * optional and give it a safe default, so validation passes and rendering
 * continues normally no matter which caller instantiates the dropdown.
 *
 * The import below resolves only on Odoo 17+, where this component exists. On
 * Odoo 16 the module path is absent, so the loader skips this asset (logged at
 * info level) and the patch is an inert no-op instead of breaking the client.
 */
import { OptionalFieldsDropdown } from "@web/views/list/optional_fields_dropdown/optional_fields_dropdown";

const DEFAULT_LIST_RENDERER_CLASS = "";

if (OptionalFieldsDropdown) {
    const props = OptionalFieldsDropdown.props;

    // OWL accepts props declared either as an array of names or as an object
    // schema; handle both shapes so the fix survives upstream refactors.
    if (Array.isArray(props)) {
        const withoutRequired = props.filter(
            (name) => name !== "listRendererClass" && name !== "listRendererClass?"
        );
        withoutRequired.push("listRendererClass?");
        OptionalFieldsDropdown.props = withoutRequired;
    } else if (props && typeof props === "object") {
        OptionalFieldsDropdown.props = {
            ...props,
            listRendererClass: { type: String, optional: true },
        };
    }

    const currentDefaults = OptionalFieldsDropdown.defaultProps || {};
    OptionalFieldsDropdown.defaultProps = {
        ...currentDefaults,
        listRendererClass:
            currentDefaults.listRendererClass ?? DEFAULT_LIST_RENDERER_CLASS,
    };
}
