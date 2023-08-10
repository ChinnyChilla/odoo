/** @odoo-module **/

import { registerModel } from '@mail/model/model_core';
import { attr, many, one } from '@mail/model/model_field';
import { clear, insert } from '@mail/model/model_field_command';
import { str_to_datetime } from 'web.time';

registerModel({
	name: 'Suggestion',
	modelMethods: {
		convertData(data) {
			var data2 = {}
			if ('id' in data) {
				data2.id = data.id
			}
			if ('can_write' in data) {
				data2.canWrite = data.can_write
			}
			if ('same_as_creator' in data) {
				data2.sameAsCreator = data.same_as_creator
			}
			if ('date_created' in data) {
				data2.dateCreated = moment(str_to_datetime(data.date_created));
			}
			if ('user_id' in data) {
				if (!data.user_id) {
					data2.suggestor = clear();
				} else {
					data2.suggestor = insert({
						id: data.user_id[0],
						display_name: data.user_id[1],
					});
				}
			}
			if ('edits' in data) {
				var temp_id=0
				data2.edits = data.edits
				for (var i = 0; i < data.edits.length; i++) {
					data2.edits[i]['id'] = temp_id
					temp_id += 1
				}
			}
			return data2
		}
	},
	recordMethods: {
		async deleteServerRecord() {
			await this.messaging.rpc({
				model: 'suggest.suggestion',
				method: 'unlink',
				args: [[this.id]],
			});
			if (!this.exists()) {
				return;
			}
			this.delete()
		},
		async saveServerRecord() {
			await this.messaging.rpc({
				model: 'suggest.suggestion',
				method: 'saveRecord',
				args: [[this.id]],
			});
			if (!this.exists()) {
				return;
			}
			this.delete()
			location.reload()
		},
	},
	fields: {
		suggestionViews: many('SuggestionView', {
			inverse: 'suggestion',
		}),
		thread: one('Thread', {
			inverse: 'suggestions',
		}),
		suggestor: one('User', {
			inverse: 'suggestionsAsSuggestor',
		}),
		id: attr({
			identifying: true,
		}),
		dateCreated: attr(),
		canWrite: attr({
			default: false,
		}),
		sameAsCreator: attr({
			default: false,
		}),
		edits: attr(),
	},
})

