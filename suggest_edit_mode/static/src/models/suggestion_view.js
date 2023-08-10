/** @odoo-module **/

import { registerModel } from '@mail/model/model_core';
import { attr, one } from '@mail/model/model_field';
import { clear } from '@mail/model/model_field_command';

registerModel({
	name: 'SuggestionView',
	fields: {
		suggestion: one('Suggestion', {
			identifying: true,
			inverse: 'suggestionViews',
		}),
		suggestionBoxView: one('SuggestionBoxView', {
			identifying: true,
			inverse: 'suggestionViews',
		}),
		dateFromNow: attr({
			compute() {
				if (!this.suggestion) {
					return clear();
				}
				if (!this.suggestion.dateCreated) {
					return clear();
				}
				return this.suggestion.dateCreated.fromNow();
			},
		}),
	},
	recordMethods: {
		onClickAccept() {
			this.suggestion.saveServerRecord();
		},
		onClickReject() {
			this.suggestion.deleteServerRecord();
		}
	}

})

