/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { clear } from '@mail/model/model_field_command';
import { one } from '@mail/model/model_field';

const session = require('web.session');

registerPatch({
	name: 'Chatter',
	recordMethods: {
		async showSuggestionPage(ev) {
			await this.topbar.checkSuggestionInherit()
			if (this.suggestionBoxView) {
				this.suggestionBoxView.update({ isSuggestionViewActive: !this.isSuggestionViewActive });
			}
			if (this.thread) {
				this.thread.fetchData(['suggestions'])
			}
            await this.messaging.rpc({
                model: 'res.users',
                method: 'switch_suggest_mode',
                args: [[session.uid]],
            });
			location.reload()
		},
		async refresh() {
			const requestData = ['activities', 'followers', 'suggestedRecipients', 'suggestions'];
			if (this.hasMessageList) {
				requestData.push('attachments', 'messages');
			}
			this.thread.fetchData(requestData);
		},
	},
	fields: {
		suggestionBoxView: one('SuggestionBoxView', {
			compute() {
				if (this.thread && this.thread.hasSuggestions && this.thread.suggestions.length > 0) {
					return {};
				}
				return clear();
			},
			inverse: 'chatter',
		}),	
	}
})

