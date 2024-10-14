# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from warnings import filters
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class VehicleLog(Document):
    def validate(self):
        if flt(self.odometer) < flt(self.last_odometer):
            frappe.throw(
                _("Current Odometer Value should be greater than Last Odometer Value {0}").format(self.last_odometer)
            )

        self.set_totals()

    def on_submit(self):
        frappe.db.set_value("Vehicle", self.license_plate, "last_odometer", self.odometer)

    def on_cancel(self):
        distance_travelled = self.odometer - self.last_odometer
        if distance_travelled > 0:
            updated_odometer_value = (
                int(frappe.db.get_value("Vehicle", self.license_plate, "last_odometer")) - distance_travelled
            )
            frappe.db.set_value("Vehicle", self.license_plate, "last_odometer", updated_odometer_value)

    @frappe.whitelist()
    def set_totals(self):
        for d in self.get("trips"):
            d.total_fuel_cost = flt(d.fuel_qty) * flt(d.price)

        self.fuel_qty = sum(flt(d.fuel_qty) for d in self.get("trips")) or 0
        self.price = (
            sum(flt(d.price) for d in self.get("trips")) / len(self.get("trips")) if len(self.get("trips")) > 0 else 0
        )
        self.total_distance = flt(self.odometer) - self.last_odometer
        self.total_fuel_cost = self.fuel_qty * self.price

    @frappe.whitelist()
    def get_delivery_trip(self):
        if self.date:
            delivery_trips = frappe.db.get_all(
                "Delivery Trip", filters={"vehicle":self.license_plate,"date":self.date}, fields=["name", "departure_time"]
            )
            trips = []
            if delivery_trips:
                for d in delivery_trips:

                        trips.append({"delivery_trip": d.name})

                self.set("trips", trips)
            else:
                frappe.msgprint(_("No delivery trips found"))


@frappe.whitelist()
def make_expense_claim(docname):
    # frappe.throw(str(docname))
    expense_claim = frappe.db.exists("Expense Claim", {"vehicle_log": docname})
    if expense_claim:
        frappe.throw(_("Expense Claim {0} already exists for the Vehicle Log").format(expense_claim))

    vehicle_log = frappe.get_doc("Vehicle Log", docname)
    # service_expense = sum([flt(d.expense_amount) for d in vehicle_log.service_detail])

    claim_amount = flt(vehicle_log.price) * flt(vehicle_log.fuel_qty) or 1
    if not claim_amount:
        frappe.throw(_("No additional expenses has been added"))

    exp_claim = frappe.new_doc("Expense Claim")
    exp_claim.employee = vehicle_log.employee
    exp_claim.vehicle_log = vehicle_log.name
    exp_claim.remark = _("Expense Claim for Vehicle Log {0}").format(vehicle_log.name)
    exp_claim.append(
        "expenses",
        {
            "expense_date": vehicle_log.date,
            "description": _("Fuel Expenses"),
            "amount": claim_amount,
            "vehicle": vehicle_log.license_plate,
        },
    )
    for row in vehicle_log.service_detail:
        exp_claim.append(
            "expenses",
            {
                "expense_date": vehicle_log.date,
                "description": _(row.service_item) + " " + _(row.type),
                "amount": row.expense_amount,
                "vehicle": vehicle_log.license_plate,
            },
        )

    return exp_claim.as_dict()
