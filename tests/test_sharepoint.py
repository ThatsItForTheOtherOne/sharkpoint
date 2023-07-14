import sharkpoint


def test_get_instance_sharepoint(sharepoint_instance, azure_identity):
    sharkpoint.SharePoint(sharepoint_instance, azure_identity)


def test_get_site_sharepoint(sharepoint_instance, azure_identity):
    instance = sharkpoint.SharePoint(sharepoint_instance, azure_identity)
    site = instance.get_site("Sharepoint LibTesting")
    assert site.site_name == "Sharepoint LibTesting"


def test_description_sharepoint(sharepoint_instance, azure_identity):
    instance = sharkpoint.SharePoint(sharepoint_instance, azure_identity)
    site = instance.get_site("Sharepoint LibTesting")
    test = site.description
    assert test != None


def test_subsites_sharepoint(sharepoint_instance, azure_identity):
    instance = sharkpoint.SharePoint(sharepoint_instance, azure_identity)
    site = instance.get_site("Sharepoint LibTesting")
    assert site != None