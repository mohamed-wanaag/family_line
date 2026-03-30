{
    'name': 'Family Hierarchy Management System',
    'version': '17.0.1.0.0',
    'category': 'Social',
    'summary': 'Manage family members, relationships, and life events',
    'description': """
        Family Hierarchy Management System
        ====================================
        - People Management (CRUD)
        - Parent-Child Hierarchy
        - Relationship Management (spouse, sibling, etc.)
        - Life Event Tracking (birth, marriage, death, etc.)
        - Search and Filtering
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'mail', 'web_hierarchy'],
    'data': [
        'security/ir.model.access.csv',
        #'security/family_security.xml',
        'views/family_person_views.xml',
        'views/family_menus.xml',
        'static/src/js/family_org_chart.js',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
