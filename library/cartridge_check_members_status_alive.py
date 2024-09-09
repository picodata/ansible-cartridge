from ansible.module_utils.helpers import Helpers as helpers

argument_spec = {
    'console_sock': {'required': True, 'type': 'str'},
}

def check_members_status_alive(params):
    console_sock = params['console_sock']

    control_console = helpers.get_control_console(console_sock)

    bad_members, err = control_console.eval_res_err('''
        local membership = require('membership')
        local members = membership.members()

        local bad_members = {}

        for _, member in pairs(members) do
            if (member.status ~= 'alive') then
                table.insert(bad_members, string.format(
                    '%s status is %s',
                    member.uri, member.status
                ))
            end
        end

        return bad_members
    ''')

    if err is not None:
        return helpers.ModuleRes(failed=True, msg=err)

    if bad_members:
        return helpers.ModuleRes(failed=True, msg="Some instances aren't alive: %s" % ', '.join(sorted(bad_members)))

    return helpers.ModuleRes(changed=False)


if __name__ == '__main__':
    helpers.execute_module(argument_spec, check_members_status_alive)
