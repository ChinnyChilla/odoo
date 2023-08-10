/** @odoo-module **/


import { registerPatch } from '@mail/model/model_core';
import { many } from '@mail/model/model_field';
registerPatch({
	name: 'User',
	recordMethods: {

	},
	fields: {
		suggestionsAsSuggestor: many('Suggestion', {
			inverse: 'suggestor',
		})
	}

})

