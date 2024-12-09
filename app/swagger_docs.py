sign_up_docs = {
    'tags': ['Authentication'],
    'description': 'User registration',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string',
                        'format': 'email',
                        'description': 'User email',
                        'example': 'john.doe@example.com'
                    },
                    'password': {
                        'type': 'string',
                        'description': 'User password',
                        'minLength': 6,
                        'maxLength': 20,
                        'pattern': '^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d]{6,20}$',
                        'example': 'Xjkds61-'
                    }
                },
                'required': ['email', 'password']
            }
        }
    ],
    'responses': {
        '201': {'description': 'User created successfully'},
        '400': {'description': 'User already exists or invalid input'}
    }
}
log_in_docs = {
    'tags': ['Authentication'],
    'description': 'User login',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string',
                        'format': 'email',
                        'description': 'User email',
                        'example': 'john.doe@example.com'
                    },
                    'password': {
                        'type': 'string',
                        'description': 'User password',
                        'minLength': 6,
                        'maxLength': 20,
                        'pattern': '^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d]{6,20}$',
                        'example': 'Xjkds61-'
                    }
                },
                'required': ['email', 'password']
            }
        }
    ],
    'responses': {
        '201': {'description': 'User created successfully'},
        '400': {'description': 'User already exists or invalid input'}
    }
}

hubspot = {
    'tags': ['Hubspot urls'],
    'description': 'Hubspot auth and callback',
}