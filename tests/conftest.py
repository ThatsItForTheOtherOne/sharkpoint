import pytest
import azure.identity
import os


@pytest.fixture(scope="session", autouse=True)
def azure_identity():
    if os.getenv("client_id") is not None:
        return azure.identity.CertificateCredential(
            tenant_id=os.getenv("tenant_id"),
            client_id=os.getenv("client_id"),
            certificate_path=os.getenv("certificate_path"),
        )
    else:
        return azure.identity.DefaultAzureCredential()


@pytest.fixture()
def sharepoint_instance():
    return os.getenv("url")
