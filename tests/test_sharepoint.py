import io
import sharkpoint
import random

def test_get_instance_sharepoint(sharepoint_instance, azure_identity):
    sharkpoint.SharePoint(sharepoint_instance, azure_identity)


def test_get_site_sharepoint(sharepoint_instance, azure_identity):
    instance = sharkpoint.SharePoint(sharepoint_instance, azure_identity)
    site = instance.get_site("Sharepoint LibTesting")
    assert site.name == "Sharepoint LibTesting"


def test_description(sharepoint_instance, azure_identity):
    instance = sharkpoint.SharePoint(sharepoint_instance, azure_identity)
    site = instance.get_site("Sharepoint LibTesting")
    assert type(site.description) is str


def test_subsites(sharepoint_instance, azure_identity):
    instance = sharkpoint.SharePoint(sharepoint_instance, azure_identity)
    site = instance.get_site("Sharepoint LibTesting")
    site = site.get_subsite("Test2")
    assert site.name == "Test2"


def test_libraries(sharepoint_instance, azure_identity):
    instance = sharkpoint.SharePoint(sharepoint_instance, azure_identity)
    site = instance.get_site("Sharepoint LibTesting")
    assert "Shared Documents" in site.libraries

def test_bytes_file(sharepoint_instance, azure_identity):
    rand_file_name = f"{random.randint(1, 100)}.txt"
    instance = sharkpoint.SharePoint(sharepoint_instance, azure_identity)
    site = instance.get_site("Sharepoint LibTesting")
    random_bytes = random.randbytes(256)
    
    with site.open(f"Shared Documents/{rand_file_name}", mode="wb") as file:
        file.write(random_bytes)

    with site.open(f"Shared Documents/{rand_file_name}", mode="rb") as file:
        assert file.getvalue() == random_bytes
    
    with site.open(f"Shared Documents/{rand_file_name}", mode="r+b") as file:
        file.seek(128, 0)
        file.write(random_bytes)
    
    with site.open(f"Shared Documents/{rand_file_name}", mode="rb") as file:
        test = io.BytesIO()
        test.write(random_bytes)
        test.seek(128, 0)
        test.write(random_bytes)
        assert test.getvalue() == file.getvalue()

def test_string_file(sharepoint_instance, azure_identity):
    rand_file_name = f"{random.randint(1, 100)}.txt"
    instance = sharkpoint.SharePoint(sharepoint_instance, azure_identity)
    site = instance.get_site("Sharepoint LibTesting")
    random_str = f"{random.randint(1, 100)}\n"
    
    with site.open(f"Shared Documents/{rand_file_name}", mode="w") as file:
        file.write(random_str)

    with site.open(f"Shared Documents/{rand_file_name}", mode="r") as file:
        assert file.getvalue() == random_str
    
    with site.open(f"Shared Documents/{rand_file_name}", mode="r+") as file:
        file.write(random_str)
        file.write(random_str)

    with site.open(f"Shared Documents/{rand_file_name}", mode="r") as file:
        test = io.StringIO()
        test.write(random_str)
        test.write(random_str)

        assert test.getvalue() == file.getvalue()

