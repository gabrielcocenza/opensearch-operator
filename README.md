# Charmed OpenSearch Operator

## Description

The Charmed OpenSearch Operator delivers automated operations management from day 0 to day 2 on the [OpenSearch](https://github.com/opensearch-project/OpenSearch) and makes it easy to ingest, search, visualize, and analyze your data.

## Usage

Until the OpenSearch Machine Charm is published, you need to follow the build & deploy instructions from [CONTRIBUTING.md](https://github.com/canonical/mongodb-operator/blob/main/CONTRIBUTING.md) to deploy the charm.

After building the charm you may deploy a single unit of OpenSearch using its default configuration
```shell
juju deploy ./opensearch_ubuntu-20.04-amd64.charm
```

## Relations

Supported [relations](https://juju.is/docs/olm/relations):

There are currently no supported relations.

## Contributing

Please see the [Juju SDK docs](https://juju.is/docs/sdk) for guidelines on enhancements to this
charm following best practice guidelines, and
[CONTRIBUTING.md](https://github.com/canonical/opensearch-operator/blob/main/CONTRIBUTING.md) for developer
guidance.
