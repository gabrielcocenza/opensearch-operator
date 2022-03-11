#!/usr/bin/env python3
"""Charm code for OpenSearch service."""
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
from pathlib import Path
from subprocess import CalledProcessError, check_call
from tokenize import Name
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader
from ops.charm import CharmBase, RelationEvent, RelationJoinedEvent
from ops.framework import StoredState
from ops.main import main
from ops.model import BlockedStatus, ModelError, Relation

logger = logging.getLogger(__name__)

PEER = "opensearch"

# TODO: change it to the right location after having the snap or
#  debian package
CONFIG_PATH = "/home/ubuntu/"

CONFIG_MAP = {
    "jvm.options": {"cmd": None, "config_path": CONFIG_PATH, "chmod": 0o660},
    "sysctl.conf": {"cmd": "sysctl -p", "config_path": "/etc/", "chmod": 0o644},
    "opensearch.yml": {"cmd": None, "config_path": CONFIG_PATH, "chmod": 0o660},
}


class OpenSearchCharm(CharmBase):
    """Charm the service."""

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(
            self.on.opensearch_relation_changed, self._opensearch_relation_changed
        )
        self.framework.observe(self.on.client_relation_joined, self._client_relation_handler)
        self.framework.observe(self.on.client_relation_changed, self._client_relation_handler)

    @property
    def _peers(self) -> Optional[Relation]:
        """Fetch the peer relation.

        Returns:
            Optional[Relation]: An `ops.model.Relation` object representing the peer
                relation.
        """
        return self.model.get_relation(PEER)

    @property
    def _unit_ips(self) -> List[str]:
        """Retrieve IP addresses associated with OpenSearch application.

        Returns:
            List[str]: a list of IP address associated with OpenSearch application.
        """
        peer_addresses = [
            str(self._peers.data[unit].get("private-address")) for unit in self._peers.units
        ]

        logger.debug(f"peer addresses: {peer_addresses}")
        self_address = self._unit_ip
        logger.debug(f"unit address: {self_address}")
        addresses = []
        if peer_addresses:
            addresses.extend(peer_addresses)
        addresses.append(self_address)
        return addresses

    @property
    def _unit_ip(self) -> str:
        """Retrieve IP addresses associated with OpenSearch unit.

        Returns:
            str: IP address of the unit
        """

        return str(self.model.get_binding(PEER).network.bind_address)

    def _get_context(self) -> Dict[str, Any]:
        """Get variables context necessary to render configuration templates.

        Returns:
            Dict[str, Any]: Dictionary containing the variables to be used on
            jinja2 templates
        """
        context = dict(self.model.config)
        context["unit_ips"] = self._unit_ips
        context["network_host"] = self._unit_ip
        context["node_name"] = self.unit.name

        return context

    def _on_config_changed(self, _):
        """Render templates for configuration."""
        self._security()
        context = self._get_context()
        for template in CONFIG_MAP.keys():
            config_path = CONFIG_MAP[template].get("config_path")
            cmd = CONFIG_MAP[template].get("cmd")
            chmod = CONFIG_MAP[template].get("chmod")
            self._write_config(config_path, template, context, chmod)
            if cmd:
                try:
                    check_call(cmd.split())
                except CalledProcessError as e:
                    logger.exception(f"Failed to run command {cmd}: {e}")
                    raise

        # update client relation data
        client_relation = self.model.get_relation("client")
        if client_relation:
            logger.info("Updating `client` relation data.")
            client_relation.data[self.unit].update(
                {
                    "cluster_name": self.model.config.get("cluster_name"),
                    "port": "9200",
                }
            )

    def _write_config(
        self,
        config_path: str,
        template: str,
        context: Dict[str, Any],
        chmod: int,
        templates_folder: str = "templates",
    ) -> None:
        """Render and write jinja2 templates for Opensearch configuration.

        Args:
            config_path (str): path for the config file.
            template (str): template name.
            context (Dict[str, Any]): variables to render on templates.
            chmod (int): chmod of the file.
            templates_folder (str, optional): Path to the folder that has the templates.
                Defaults to "templates".
        """
        target = Path(config_path) / template
        rendered_template = Environment(loader=FileSystemLoader(templates_folder)).get_template(
            template
        )
        target.write_text(rendered_template.render(context))
        target.chmod(chmod)

    def _opensearch_relation_changed(self, event: RelationEvent) -> None:
        """Add unit to the cluster by configuring the file opensearch.yml.

        Args:
            event (RelationEvent): The triggering relation changed event.
        """
        context = self._get_context()
        config_path = CONFIG_MAP["opensearch.yml"].get("config_path")
        chmod = CONFIG_MAP["opensearch.yml"].get("chmod")
        self._write_config(config_path, "opensearch.yml", context, chmod)

    def _client_relation_handler(self, event: RelationJoinedEvent) -> None:
        """Set the cluster name and port through the relation.

        Args:
            event (RelationJoinedEvent): The triggering relation joined event.
        """
        event.relation.data[self.unit].update(
            {
                "cluster_name": self.model.config.get("cluster_name"),
                "port": "9200",
            }
        )

    def _security(self):
        resources = ["tls_ca", "tls_key", "admin_key"]
        try:
            resources_path = [self.model.resources.fetch(resource) for resource in resources]
        except NameError as e:
            self.unit.status = BlockedStatus(f"Missing resource: {e}")
            return

        # copy the files to the config path
        for resource_path in resources_path:
            target = Path(CONFIG_PATH) / resource_path.name
            if not target.exists():
                target.write_text(resource_path.open().read())

        # generate node certificate


if __name__ == "__main__":
    main(OpenSearchCharm)
