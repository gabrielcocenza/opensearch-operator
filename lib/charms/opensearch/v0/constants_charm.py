# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""In this file we declare the constants and enums used by the charm."""

# The unique Charmhub library identifier, never change it
LIBID = "a8e3e482b22f4552ad6211ea77b46f7b"

# Increment this major API version when introducing breaking changes
LIBAPI = 0

# Increment this PATCH version before using `charmcraft publish-lib` or reset
# to 0 if you are raising the major API version
LIBPATCH = 1


# Blocked statuses
WaitingToStart = "Waiting for OpenSearch to start..."
InstallError = "Could not install OpenSearch."
CertsExpirationError = "The certificates: {} need to be refreshed."
WaitingForBusyShards = "The shards: {} need to complete building."
ExclusionFailed = "The {} exclusion(s) of this node failed."
AllocationExclusionFailed = "The exclusion of this node from the allocations failed."
VotingExclusionFailed = "The exclusion of this node from the voting list failed."
ServiceStartError = "An error occurred during the start of the OpenSearch service."
ServiceStopped = "The OpenSearch service stopped."
ServiceStopFailed = "An error occurred while attempting to stop the OpenSearch service."
ServiceIsStopping = "The OpenSearch service is stopping."
TLSNotFullyConfigured = "Waiting for TLS to be fully configured..."
TLSRelationBrokenError = (
    "Relation broken with the TLS Operator while TLS not fully configured. Stopping OpenSearch."
)
NoNodeUpInCluster = "No node is up in this cluster."
TooManyNodesRemoved = (
    "Too many nodes being removed at the same time, please scale your application up."
)
ClusterHealthRed = "1 or more 'primary' shards are not assigned, please scale your application up."
ClusterHealthYellow = (
    "1 or more 'replica' shards are not assigned, please scale your application up."
)

# Wait status
RequestUnitServiceOps = "Requesting lock on operation: {}"

# Maintenance statuses
InstallProgress = "Installing OpenSearch..."
SecurityIndexInitProgress = "Initializing the security index..."
AdminUserInitProgress = "Configuring admin user..."
HorizontalScaleUpSuggest = "Horizontal scale up advised: {} shards unassigned."
WaitingForOtherUnitServiceOps = "Waiting for other units to complete the ops on their service."
