register_schema = {'username': {'type': 'string', 'required': True},
                   'password': {'type': 'string', 'required': True}}

register_therapist_schema = {'username': {'type': 'string', 'required': True},
                            'password': {'type': 'string', 'required': True},
                            'occupation': {'type': 'string', 'required': True}}

login_schema = {'username': {'type': 'string', 'required': True},
                'password': {'type': 'string', 'required': True}}

restriction_schema = {'start_time': {'type': 'integer', 'required': True},
                      'end_time': {'type': 'integer', 'required': True},
                      'description': {'type': 'string', 'required': False}}

occupation_schema = {'occupation_name': {'type': 'string', 'required': True}}

therapist_schema = {'therapist_id': {'type': 'string', 'required': True}}
