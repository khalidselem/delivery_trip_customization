// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

let fields_to_refresh = [
	"odometer",
	"last_odometer",
	"trips",
	"fuel_qty",
	"price",
	"total_distance",
	"total_fuel_cost",
] ;
frappe.ui.form.on("Vehicle Log", {
	refresh: function (frm) {
		if (frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Expense Claim'), function () {
				frm.events.expense_claim(frm);
			}, __('Create'));
			frm.page.set_inner_btn_group_as_primary(__('Create'));
		}
	},
	odometer(frm) {
		frm.events.set_totals(frm);
	},
	last_odometer(frm) {
		frm.events.set_totals(frm);
	},
	fuel_qty(frm) {
		frm.events.set_totals(frm);
	},
	price(frm) {
		frm.events.set_totals(frm);
	},
	total_distance(frm) {
		frm.events.set_totals(frm);
	},
	total_fuel_cost(frm) {
		frm.events.set_totals(frm);
	},
	set_totals(frm) {
		frappe.call({
			doc: frm.doc,
			method: "set_totals",
			callback: function (r) {
				frm.refresh_fields(fields_to_refresh);
			}
		});
	},

	get_trips(frm) {
		// frm.clear_table("items");
		frappe.call({
			doc: frm.doc,
			method: "get_delivery_trip",
			callback: function (r) {
				frm.refresh_field("trips");
			}
		});
	},

	expense_claim: function (frm) {
		frappe.call({
			method: "delivery_trip_customization.delivery_trip_customization.doctype.vehicle_log.vehicle_log.make_expense_claim",
			args: {
				docname: frm.doc.name
			},
			callback: function (r) {
				var doc = frappe.model.sync(r.message);
				frappe.set_route('Form', 'Expense Claim', r.message.name);
			}
		});
	}
});

frappe.ui.form.on('Vehicle Log Trips', {
	trips_add: function (frm) {
		frm.events.set_totals(frm);
	},

	fuel_qty: function (frm) {
		frm.events.set_totals(frm);
	},

	price: function (frm) {
		frm.events.set_totals(frm);
	},

	trips_remove: function (frm) {
		frm.events.set_totals(frm);
	},
});