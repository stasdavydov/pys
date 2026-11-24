
import pytest
from google.auth.credentials import AnonymousCredentials
from google.cloud import storage
from testcontainers.core.container import DockerContainer

from pys.gcs import Storage


@pytest.fixture(scope="session")
def gcs_client():
    with (
        DockerContainer("fsouza/fake-gcs-server")
        .with_command("-scheme http -port 4443 -backend memory")
        .with_exposed_ports(4443)
    ) as container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(4443)
        endpoint = f"http://{host}:{port}"

        client = storage.Client(
            project="test-project",
            credentials=AnonymousCredentials(),
            client_options={"api_endpoint": endpoint},
        )

        client.create_bucket("test-bucket")

        yield client

        client.close()


@pytest.fixture
def gcs_storage(gcs_client, tmp_path):
    # Unique prefix for every test.
    prefix = f"tests/{tmp_path.name}/"

    instance = Storage(
        bucket="test-bucket",
        prefix=prefix,
        client=gcs_client,
    )

    yield instance

    instance.destroy()
