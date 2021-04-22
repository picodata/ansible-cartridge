#!/usr/bin/env python

from ansible.module_utils.helpers import Helpers as helpers

argument_spec = {
    'hostvars': {'required': True, 'type': 'dict'},
}

FACTS_BY_TARGETS = {
    'validate_config': [
        'all_rw',
        'cartridge_app_config',
        'cartridge_app_install_dir',
        'cartridge_app_instances_dir',
        'cartridge_app_group',
        'cartridge_app_name',
        'cartridge_app_user',
        'cartridge_auth',
        'cartridge_bootstrap_vshard',
        'cartridge_cluster_cookie',
        'cartridge_conf_dir',
        'cartridge_configure_systemd_unit_files',
        'cartridge_configure_tmpfiles',
        'cartridge_control_instance',
        'cartridge_custom_scenarios',
        'cartridge_custom_steps',
        'cartridge_custom_steps_dir',
        'cartridge_data_dir',
        'cartridge_defaults',
        'cartridge_delivered_package_path',
        'cartridge_enable_tarantool_repo',
        'cartridge_failover',
        'cartridge_failover_params',
        'cartridge_failover_promote_params',
        'cartridge_install_tarantool_for_tgz',
        'cartridge_keep_num_latest_dists',
        'cartridge_memtx_dir_parent',
        'cartridge_multiversion',
        'cartridge_package_path',
        'cartridge_remove_temporary_files',
        'cartridge_run_dir',
        'cartridge_scenario',
        'cartridge_scenario_name',
        'cartridge_systemd_dir',
        'cartridge_tmpfiles_dir',
        'cartridge_vinyl_dir_parent',
        'cartridge_wait_buckets_discovery',
        'cartridge_wal_dir_parent',
        'config',
        'twophase_netbox_call_timeout',
        'twophase_upload_config_timeout',
        'twophase_apply_config_timeout',
        'edit_topology_timeout',
        'edit_topology_healthy_timeout',
        'expelled',
        'failover_priority',
        'instance_discover_buckets_timeout',
        'instance_start_timeout',
        'replicaset_alias',
        'restarted',
        'roles',
        'stateboard',
        'vshard_group',
        'weight',
        'zone',
        'cartridge_eval_body',
        'cartridge_eval_args',
        'cartridge_eval_file',
    ],
    'single_instances_for_each_machine': [
        'expelled',
        'ansible_host',
    ],
    'connect_to_membership': [
        'expelled',
        'stateboard',
        'config',
    ],
    'not_expelled_instance': [
        'expelled',
        'stateboard',
        'instance_info',
    ],
    'control_instance': [
        'expelled',
        'stateboard',
        'config',
        'replicaset_alias',
        'cartridge_run_dir',
    ],
    'edit_topology': [
        'expelled',
        'stateboard',
        'replicaset_alias',
        'roles',
        'failover_priority',
        'all_rw',
        'weight',
        'vshard_group',
        'zone',
        'config',
    ],
}


def get_cached_facts(params):
    hostvars = params['hostvars']

    facts = {}
    for instance_name, instance_vars in hostvars.items():
        role_vars = hostvars[instance_name].get('role_facts', {})

        for target, fact_names in FACTS_BY_TARGETS.items():
            facts[target] = facts.get(target, {})
            facts[target][instance_name] = facts[target].get(instance_name, {})

            for fact_name in fact_names:
                if fact_name in role_vars:
                    facts[target][instance_name][fact_name] = role_vars[fact_name]
                elif fact_name in instance_vars:
                    facts[target][instance_name][fact_name] = instance_vars[fact_name]

    return helpers.ModuleRes(changed=False, facts=facts)


if __name__ == '__main__':
    helpers.execute_module(argument_spec, get_cached_facts)