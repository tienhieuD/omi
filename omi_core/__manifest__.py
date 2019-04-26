{
    'name': "OMI Core",
    'author': 'Odoo Community Association (OCA)',
    'version': '11.0.1.0.0',
    'maintainer': 'Lorem',
    'website': "http://google.com",
    'license': 'LGPL-3',
    'category': 'Uncategorized',
    'sequence': 1000,
    'summary': """Lorem ipsum dolor sit amet.""",
    'depends': ['base', 'mail', 'crm', 'sale', 'note', 'im_livechat', 'crm_livechat', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'data/omi_fb_permission.xml',
        'views/assets.xml',
        'views/omi_fb_permission_view.xml',
        'views/omi_quick_reply_view.xml',
        'views/mail_channel_view.xml',
        'views/res_partner_view.xml',
        'views/res_config_settings_view.xml',
        'views/menuitem.xml',
    ],
    'demo': [],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    # 'js': ['static/src/js/first_module.js',],
    # 'css': ['static/src/css/web_example.css',],
    # 'images': ['static/description/icon.png',],
    'auto_install': False,
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [
            'facebook',
            'pymessenger',
        ]
    }
    # 'pre_init_hook': 'pre_init_hook',
    # 'post_init_hook': 'post_init_hook',
    # 'uninstall_hook': 'uninstall_hook',
}
