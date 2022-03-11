# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

import unittest
from subprocess import CalledProcessError
from unittest.mock import call, patch

from ops.testing import Harness

import charm
from charm import OpenSearchCharm
from tests.unit.helpers import patch_network_get


class TestCharm(unittest.TestCase):
    def setUp(self):
        self.harness = Harness(OpenSearchCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()
        self.peer_rel_id = self.harness.add_relation(charm.PEER, "opensearch")
        self.client_rel_id = self.harness.add_relation("client", "graylog")

    @patch_network_get()
    @patch("charm.OpenSearchCharm._write_config")
    @patch("charm.check_call")
    def test_on_config_changed(self, mock_call, mock_write_config):
        self.harness.add_relation_unit(self.client_rel_id, "graylog/0")
        with self.assertLogs("charm", "INFO") as logger:
            self.harness.update_config({"cluster_name": "foo_cluster"})

        expected_context = {
            "cluster_name": "foo_cluster",
            "os_java_opts": 3,
            "max_map_count": 262144,
            "unit_ips": ["10.6.215.1"],
            "network_host": "10.6.215.1",
            "node_name": "opensearch/0",
        }
        for template in charm.CONFIG_MAP:
            cmd = charm.CONFIG_MAP[template].get("cmd")
            if cmd:
                expected_check_call = call(cmd.split())
                self.assertIn(expected_check_call, mock_call.call_args_list)
            config_path = charm.CONFIG_MAP[template].get("config_path")
            chmod = charm.CONFIG_MAP[template].get("chmod")
            expected_write_call = call(config_path, template, expected_context, chmod)
            self.assertIn(expected_write_call, mock_write_config.call_args_list)

        # change cluster name and check if relation changed
        self.assertEqual(
            self.harness.get_relation_data(self.client_rel_id, "opensearch/0"),
            {"cluster_name": "foo_cluster", "port": "9200"},
        )
        self.assertIn("Updating `client` relation data", "".join(logger.output))

    @patch_network_get()
    @patch(
        "charm.CONFIG_MAP",
        {"bar_template": {"cmd": "foo_cmd", "config_path": "/etc/", "chmod": 0o644}},
    )
    @patch("charm.OpenSearchCharm._write_config")
    @patch("charm.check_call")
    def test_on_config_changed_error(self, mock_call, mock_write_config):
        mock_call.side_effect = CalledProcessError(1, "foo_cmd", "foo cmd error")
        with self.assertLogs("charm", "ERROR") as logger:
            with self.assertRaises(CalledProcessError):
                self.harness.charm.on.config_changed.emit()
        self.assertIn("Failed to run command foo_cmd", "".join(logger.output))

    @patch_network_get()
    @patch("charm.OpenSearchCharm._write_config")
    def test_opensearch_relation(self, mock_write):
        expected_context = {
            "cluster_name": "opensearch",
            "os_java_opts": 3,
            "max_map_count": 262144,
            "unit_ips": ["10.6.215.2", "10.6.215.1"],
            "network_host": "10.6.215.1",
            "node_name": "opensearch/0",
        }
        self.harness.add_relation_unit(self.peer_rel_id, "opensearch/1")
        self.harness.update_relation_data(
            self.peer_rel_id, "opensearch/1", {"private-address": "10.6.215.2"}
        )
        expected_call = call(charm.CONFIG_PATH, "opensearch.yml", expected_context, 0o660)
        # check that opensearch relation changed was called
        self.assertIn(expected_call, mock_write.call_args_list)

        resulting_ips = self.harness.charm._unit_ips
        expected_ips = ["10.6.215.2", "10.6.215.1"]
        self.assertEqual(resulting_ips, expected_ips)

    def test_client_relation_joined(self):
        relation_parameters = {"cluster_name": "opensearch", "port": "9200"}
        self.harness.add_relation_unit(self.client_rel_id, "graylog/0")
        self.assertEqual(
            self.harness.get_relation_data(self.client_rel_id, "opensearch/0"), relation_parameters
        )

    def test_client_relation_changed(self):
        relation_parameters = {"cluster_name": "foo_cluster", "port": "9200"}
        self.harness.add_relation_unit(self.client_rel_id, "graylog/0")
        self.harness.update_relation_data(self.client_rel_id, "opensearch/0", relation_parameters)
        self.assertEqual(
            self.harness.get_relation_data(self.client_rel_id, "opensearch/0"), relation_parameters
        )
