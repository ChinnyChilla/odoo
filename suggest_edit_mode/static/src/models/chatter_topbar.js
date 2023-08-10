/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';

registerPatch({
	name: 'ChatterTopbar',
	recordMethods: {
		async checkSuggestionInherit() {
			if (!this.chatter.thread) {
				return false
			} else {
				const testing = await this.messaging.rpc({
					model: 'mail.activity.mixin',
					method: 'check_inherit',
					args: [this.chatter.thread.model],
				}, { shadow: true })
				return testing
			}
		},
	},
});

