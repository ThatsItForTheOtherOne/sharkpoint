import io
import sharkpoint
import random
import pytest

@pytest.mark.incremental
class TestSharkpointCRUD:
    created_files_list = []
    discriminator = 28
    test_site_name = f"sharkpoint testing-{discriminator}"
    test_site_path = f"sharkpointtest-{discriminator}"
    site = None

    def test_get_instance_sharepoint(self, sharepoint_instance, azure_identity):
        sharkpoint.SharePoint(sharepoint_instance, azure_identity)

    def test_create_sharepoint_site(self, sharepoint_instance, azure_identity, tester):
        instance = sharkpoint.SharePoint(sharepoint_instance, azure_identity)
        TestSharkpointCRUD.site = instance.create_site(site_name=TestSharkpointCRUD.test_site_name, path=TestSharkpointCRUD.test_site_path, owner=tester, description="Sharkpoint Unit Test!")
        print(TestSharkpointCRUD.site._site_url)
        assert TestSharkpointCRUD.site.name == TestSharkpointCRUD.test_site_name
    
    def test_description(self):
        assert TestSharkpointCRUD.site.description == "Sharkpoint Unit Test!"

    def test_libraries(self):
        assert "Shared Documents" in TestSharkpointCRUD.site.libraries

    def test_make_directory(self):
        TestSharkpointCRUD.site.mkdir("Shared Documents/test")
        assert "test" in TestSharkpointCRUD.site.listdir("Shared Documents/")

    def test_bytes_file(self):

        rand_file_name = f"{random.randint(1, 100)}.txt"
        TestSharkpointCRUD.created_files_list.append(rand_file_name)
        random_bytes = random.randbytes(256)

        with TestSharkpointCRUD.site.open(f"Shared Documents/test/{rand_file_name}", mode="wb") as file:
            file.write(random_bytes)
            try:
                file.read(-1)
            except IOError:
                pass
            else:
                raise AssertionError()

        with TestSharkpointCRUD.site.open(f"Shared Documents/test/{rand_file_name}", mode="rb") as file:
            assert file.getvalue() == random_bytes

        with TestSharkpointCRUD.site.open(f"Shared Documents/test/{rand_file_name}", mode="r+b") as file:
            file.seek(128, 0)
            file.write(random_bytes)

        with TestSharkpointCRUD.site.open(f"Shared Documents/test/{rand_file_name}", mode="rb") as file:
            test = io.BytesIO()
            test.write(random_bytes)
            test.seek(128, 0)
            test.write(random_bytes)
            assert test.getvalue() == file.getvalue()


    def test_string_file(self):

        rand_file_name = f"{random.randint(1, 100)}.txt"
        TestSharkpointCRUD.created_files_list.append(rand_file_name)
        random_str = f"{random.randint(1, 100)}\n"

        with TestSharkpointCRUD.site.open(f"Shared Documents/test/{rand_file_name}", mode="w") as file:
            file.write(random_str)
            try:
                file.read(-1)
            except IOError:
                pass
            else:
                raise AssertionError()

        with TestSharkpointCRUD.site.open(f"Shared Documents/test/{rand_file_name}", mode="r") as file:
            assert file.read() == random_str

        with TestSharkpointCRUD.site.open(f"Shared Documents/test/{rand_file_name}", mode="r+") as file:
            file.seek(0, io.SEEK_END)
            file.write(random_str)
            file.write(random_str)

        with TestSharkpointCRUD.site.open(f"Shared Documents/test/{rand_file_name}", mode="r") as file:
            test = io.StringIO()
            test.write(random_str)
            test.write(random_str)
            test.write(random_str)
            test.seek(0)
            assert test.read() == file.read()

    def test_delete_files(self):
        for file in TestSharkpointCRUD.created_files_list:
            TestSharkpointCRUD.site.remove(f"Shared Documents/test/{file}")
        for file in TestSharkpointCRUD.created_files_list:
            assert file not in TestSharkpointCRUD.site.listdir("Shared Documents/test/")

    def test_delete_directory(self):
        TestSharkpointCRUD.site.rmdir("Shared Documents/test")
        assert "test" not in TestSharkpointCRUD.site.listdir("Shared Documents/")
