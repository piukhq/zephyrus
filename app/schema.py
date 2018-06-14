from voluptuous import Schema, Required

client_info = Schema({
    Required('organisation'): str,
    Required('client_id'): str,
    Required('secret'): str
})

client_info_list = Schema([client_info])
