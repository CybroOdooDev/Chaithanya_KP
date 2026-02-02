/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";


patch(ActionpadWidget.prototype, {

    async doSubmitOrder() {
        // 1️⃣ Call original behavior (send to kitchen)
        await super.doSubmitOrder(...arguments);

        const order = this.pos.getOrder();
        if (!order || order.isEmpty()) {
            return;
        }

        // 2️⃣ Print FULL receipt automatically
        try {
            await this.pos.printReceipt({
                order: order,
                basic: false,   // FULL receipt
            });
        } catch (error) {
            console.error("Failed to print receipt on order", error);
        }
    },

});
