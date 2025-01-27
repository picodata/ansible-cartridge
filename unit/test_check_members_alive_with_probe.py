import sys
import unittest

import module_utils.helpers as helpers
import unit.utils as utils
from unit.instance import Instance

sys.modules['ansible.module_utils.helpers'] = helpers
from library.cartridge_check_members_alive_with_probe import \
    check_members_alive_with_probe


def call_check_members_alive(console_sock, allowed_states=['RolesConfigured']):
    return check_members_alive_with_probe({
        'console_sock': console_sock,
        'allowed_states': allowed_states,
    })


def set_known_servers(instance, servers):
    instance.set_variable('known_servers', {
        s: True for s in servers
    })


URI1 = '127.0.0.1:3301'
URI2 = '127.0.0.1:3302'


class TestInstanceStarted(unittest.TestCase):
    def setUp(self):
        self.instance = Instance()
        self.console_sock = self.instance.console_sock
        self.cookie = self.instance.cluster_cookie

        self.instance.start()

    def test_no_joined_instances(self):
        set_known_servers(self.instance, [])
        self.instance.clear_calls('admin_probe_server')

        self.instance.set_membership_members([
            utils.get_member('instance-1'),
            utils.get_member('instance-2'),
            # UUID from membership doesn't matter, instances from topology conf are checked
            utils.get_member('instance-3', with_uuid=True),
        ])

        res = call_check_members_alive(self.console_sock)
        self.assertTrue(res.failed)
        self.assertIn("Instances aren't joined to cluster yet", res.msg)

        calls = self.instance.get_calls('admin_probe_server')
        self.assertEqual(len(calls), 0)

    def test_joined_instances_alive(self):
        set_known_servers(self.instance, [
            'instance-1-joined-uri',
            'instance-2-joined-uri',
            'instance-3-joined-uri',
        ])
        self.instance.clear_calls('admin_probe_server')
        self.instance.add_replicaset(
            alias='r1',
            instances=['instance-1-joined', 'instance-2-joined', 'instance-3-joined'],
        )

        self.instance.set_membership_members([
            utils.get_member('instance-1-joined', with_uuid=True,
                             status='alive', state='RolesConfigured'),
            utils.get_member('instance-2-joined', with_uuid=True,
                             status='alive', state='RolesConfigured'),
            utils.get_member('instance-3-joined', with_uuid=True,
                             status='alive', state='RolesConfigured'),
            utils.get_member('instance-4', status='dead', state='Unconfigured'),
            utils.get_member('instance-5', status='dead', state='Unconfigured'),
        ])

        res = call_check_members_alive(self.console_sock)
        self.assertFalse(res.failed, res.msg)

        calls = self.instance.get_calls('admin_probe_server')
        self.assertEqual(len(calls), 3)

    def test_bad_joined_instances(self):
        set_known_servers(self.instance, [
            'instance-1-joined-uri',
            'instance-2-joined-uri',
            'instance-3-joined-uri',
            'instance-4-joined-uri'
        ])
        self.instance.clear_calls('admin_probe_server')

        self.instance.add_replicaset(
            alias='r1',
            instances=['instance-1-joined', 'instance-2-joined',
                       'instance-3-joined', 'instance-4-joined'],
        )

        self.instance.set_membership_members([
            utils.get_member('instance-1-joined', with_uuid=True,
                             status='alive', state='RolesConfigured'),
            utils.get_member('instance-2-joined', uuid='bad-uuid',
                             status='alive', state='RolesConfigured'),
            utils.get_member('instance-3-joined', with_uuid=True,
                             status='dead', state='RolesConfigured'),
            utils.get_member('instance-4-joined', with_uuid=True,
                             status='alive', state='OperationError'),
            utils.get_member('instance-5', status='dead', state='Unconfigured'),
            utils.get_member('instance-6', status='dead', state='Unconfigured'),
        ])

        res = call_check_members_alive(self.console_sock)
        self.assertTrue(res.failed)
        self.assertEqual(
            res.msg,
            "Some instances aren't alive: "
            "instance-2-joined-uri uuid mismatch: expected instance-2-joined-uuid, have bad-uuid, "
            "instance-3-joined-uri status is dead, "
            "instance-4-joined-uri state is OperationError"
        )

        calls = self.instance.get_calls('admin_probe_server')
        self.assertEqual(len(calls), 4)

    def test_allowed_states(self):
        set_known_servers(self.instance, ['instance-1-joined-uri',
                          'instance-2-joined-uri', 'instance-3-joined-uri'])
        self.instance.clear_calls('admin_probe_server')

        self.instance.add_replicaset(
            alias='r1',
            instances=['instance-1-joined', 'instance-2-joined', 'instance-3-joined'],
        )

        self.instance.set_membership_members([
            utils.get_member('instance-1-joined', with_uuid=True,
                             status='alive', state='SomeState'),
            utils.get_member('instance-2-joined', with_uuid=True,
                             status='alive', state='SomeOtherState'),
            utils.get_member('instance-3-joined', with_uuid=True,
                             status='alive', state='OneMoreState'),
            utils.get_member('instance-4', status='dead', state='Unconfigured'),
            utils.get_member('instance-5', status='dead', state='Unconfigured'),
        ])

        res = call_check_members_alive(self.console_sock, allowed_states=[
            'SomeState', 'SomeOtherState', 'OneMoreState',
        ])
        self.assertFalse(res.failed, res.msg)

        calls = self.instance.get_calls('admin_probe_server')
        self.assertEqual(len(calls), 3)

    def tearDown(self):
        self.instance.stop()
        del self.instance
