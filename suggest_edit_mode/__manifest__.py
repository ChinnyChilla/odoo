{
    'name': 'Odoo: Suggest an Edit mode',
    'version': '1.0',
    'category': 'Base/Modifications',
    'summary': 'Adds an suggest mode to fields',
    'description': """
	      This module adds a suggest mode to fields and adds a new permission to allow users to edit fields in suggest mode.""",
    'author': 'Odoo Inc',
    'depends': ["base", "mail", "web"],
    'data': [
		'security/suggest_groups.xml',
		'security/ir.model.access.csv',
    	'views/res_users_views.xml',
    ],
    'demo': [],
    'license': 'OPL-1',
	'assets': {
		'web.assets_backend': [
			'suggest_edit_mode/static/src/scss/edit_mode.scss',
			'suggest_edit_mode/static/src/xml/*',
			'suggest_edit_mode/static/src/models/*.js',
			'suggest_edit_mode/static/src/components/*/*'
		]
	}
}

