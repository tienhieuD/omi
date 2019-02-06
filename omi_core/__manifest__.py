# -*- coding: utf-8 -*-

{
    'name': "OMI Core",
    'version': '0.1',
    'author': 'Lorem',
    'maintainer': 'Lorem',
    'website': "http://google.com",
    'license': 'LGPL-3',
    'category': 'Uncategorized',
    'sequence': 1000,
    'description': """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum""",
    'summary': """Lorem ipsum dolor sit amet.""",
    'depends': ['base', 'crm', 'sale', 'mail', 'im_livechat','crm_livechat'],
    'data': [
        'views/omi_fb_permission_view.xml',
        'views/res_config_settings_view.xml',
        'views/menuitem.xml',
    ],
    'demo': [],
    'qweb': ['static/src/xml/*.xml'],
    # 'js': ['static/src/js/first_module.js',],
    # 'css': ['static/src/css/web_example.css',],
    # 'images': ['static/description/icon.png',],
    'auto_install': False,
    'application': False,
    'installable': True,
    'external_dependencies': {'python' : ['facebook']}
    # 'pre_init_hook': 'pre_init_hook',
    # 'post_init_hook': 'post_init_hook',
    # 'uninstall_hook': 'uninstall_hook',
}
