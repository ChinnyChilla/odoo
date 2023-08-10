/** @odoo-module **/

import { registerModel } from '@mail/model/model_core';
import { attr, many, one } from '@mail/model/model_field';

registerModel({
    name: 'SuggestionBoxView',
    recordMethods: {
		onClickSuggestionBoxTitle(ev) {
			ev.preventDefault();
			this.update({ isSuggestionViewActive: !this.isSuggestionViewActive });
		},
    },
    fields: {
        chatter: one('Chatter', {
            identifying: true,
			inverse: 'suggestionBoxView',
        }),	
        isSuggestionViewActive: attr({
            default: false,
        }),
		suggestionViews: many('SuggestionView', {
			compute() {
				return this.chatter.thread.suggestions.map(suggestion => {
					return { suggestion }
				})
				
			},
			inverse: 'suggestionBoxView'
		}),
    },
});

