from azure.mgmt.resource import ResourceManagementClient
from azure.common.credentials import ServicePrincipalCredentials

subscription_id = '<your-subscription-id>'
client_id = '<your-client-id>'
client_secret = '<your-client-secret>'
tenant_id = '<your-tenant-id>'

credentials = ServicePrincipalCredentials(
    client_id=client_id,
    secret=client_secret,
    tenant=tenant_id
)

resource_client = ResourceManagementClient(credentials, subscription_id)

resource_group_name = '<your-resource-group-name>'
location = '<your-location>'

resource_group_params = {'location': location}
resource_group = resource_client.resource_groups.create_or_update(
    resource_group_name, resource_group_params
)