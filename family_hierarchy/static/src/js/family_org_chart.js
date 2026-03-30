/** @odoo-module **/
import { registry } from "@web/core/registry";
import { hrOrgChart } from "@hr_org_chart/fields/hr_org_chart";

// We extend the HR Org Chart but change the model to our custom one
export class FamilyOrgChart extends hrOrgChart {
    static template = "hr_org_chart.HrOrgChart"; // Reuse existing template
}

// Map the widget so it's usable in XML
registry.category("fields").add("family_org_chart", FamilyOrgChart);