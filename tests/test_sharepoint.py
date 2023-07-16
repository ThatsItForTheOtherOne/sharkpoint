import sharkpoint


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
