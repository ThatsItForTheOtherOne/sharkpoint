import json
from typing import Self
import requests
from . import sharepoint_file


class SharepointSite:
    """
    SharePointSite(sharepoint_site_url, sharepoint_base_url, header)

    A class used to represent a SharePoint site using the SharePoint REST API v1.
    ...

    Parameters
    ----------
    sharepoint_site_url : str
        The URL of the Sharepoint site
    sharepoint_base_url : str
        The URL of the Sharepoint instance
    header : dict
        The header for requests made to the API containing the Bearer token

    Attributes
    ----------
    name : str
        The user-facing name of the Sharepoint site
    description : str
        The description of the Sharepoint site
    subsites : dict
        A dict of SharePoint subsites, user-facing name is key and url is value
    libraries : list[str]
        A list of strings of Sharepoint document library names

    Methods
    -------
    listdir(path)
        Returns a list of directories in a document library
    mkdir(path)
        Creates a new directory in a document library
    open(path, checkout = False)
        Downloads a file from a document library and returns a SharepointFile object
    get_subsite(site_name)
        Returns a SharepointSite object for a subsite
    rmdir(path)
        Removes a directory in a document library
    remove(path)
        Removes a file in a document library
    """

    def __init__(
        self,
        sharepoint_site_url: str,
        sharepoint_base_url: str,
        header,
    ) -> None:
        self._site_url = sharepoint_site_url
        self._base_url = sharepoint_base_url
        self._header = header

    @property
    def libraries(self):
        api_url = f"{self._site_url}/_api/web/lists?$select=Title,ServerRelativeUrl&$filter=BaseTemplate eq 101 and hidden eq false&$expand=RootFolder"
        request = requests.get(api_url, headers=self._header)
        request = json.loads(request.content)

        request = request["d"]["results"]
        libraries = [library["RootFolder"]["Name"] for library in request]

        return libraries

    def _file_and_directory_list(self, path: str):
        path_list = path.split("/")
        path_list = list(filter(None, path_list))

        if path_list[0] not in self.libraries:
            raise FileNotFoundError(f"Document Library {path_list[0]} Not Found.")

        api_url = f"{self._site_url}/_api/web/GetFolderByServerRelativeUrl('{'/'.join(path_list)}')?$expand=Folders,Files"
        request = requests.get(api_url, headers=self._header)
        request = json.loads(request.content)

        if "error" in request:
            error_code = request["error"]["code"]
            if error_code == "-2147024894, System.IO.FileNotFoundException":
                raise FileNotFoundError(request["error"]["message"]["value"])
            else:
                raise Exception(request["error"]["message"]["value"])

        request = request["d"]
        files = request["Files"]["results"]
        folders = request["Folders"]["results"]

        return [file["Name"] for file in files], [folder["Name"] for folder in folders]

    def list_files(self, path: str) -> list[str]:
        """List all files in a directory on a SharePoint document library.

        Parameters
        ----------
        path : str
            The path of the directory to search, relative to the site as a whole. File paths are UNIX-like.

        Raises
        ------
        FileNotFoundError
            If the document library does not exist or if a nonexistent folder is searched.
        Exception
            If an API error has occured that is not otherwise caught.

        Returns
        -------
        list
            List of files
        """

        files_list, _ = self._file_and_directory_list(path)
        return files_list

    def listdir(self, path: str) -> list[str]:
        """List all files and folders in a directory on a SharePoint document library.

        Parameters
        ----------
        path : str
            The path of the directory to search, relative to the site as a whole. File paths are UNIX-like.

        Raises
        ------
        FileNotFoundError
            If the document library does not exist or if a nonexistent folder is searched.
        Exception
            If an API error has occured that is not otherwise caught.

        Returns
        -------
        list
            List of files and directories
        """
        files_list, folders_list = self._file_and_directory_list(path)
        return files_list + folders_list

    def mkdir(self, path: str) -> None:
        """Create a new directory on a SharePoint document library.

        Parameters
        ----------
        path : str
            The path of the directory to create, relative to the site as a whole. File paths are UNIX-like.

        Raises
        ------
        FileExistsError
            If the folder already exists.
        FileNotFoundError
            If the document library does not exist or if a subfolder is attempted to be made in a nonexistent folder.
        Exception
            If an API error has occured that is not otherwise caught.
        """

        path_list = path.split("/")
        path_list = list(filter(None, path_list))

        if path_list[0] not in self.libraries:
            raise FileNotFoundError(f"Document Library {path_list[0]} not found.")

        if path_list[-1] in self.listdir("/".join(path_list[:-1])):
            raise FileExistsError(f"Folder {path_list[-1]} exists.")

        api_url = f"{self._site_url}/_api/web/folders"
        payload = json.dumps(
            {
                "__metadata": {"type": "SP.Folder"},
                "ServerRelativeUrl": "/".join(path_list),
            }
        )

        request = requests.post(url=api_url, data=payload, headers=self._header)
        request = json.loads(request.content)

        if "error" in request:
            error_code = request["error"]["code"]
            if error_code == "-2130247139, Microsoft.SharePoint.SPException":
                raise FileNotFoundError(request["error"]["message"]["value"])
            else:
                raise Exception(request["error"]["message"]["value"])

    def rmdir(self, path: str) -> None:
        """Delete a directory on a SharePoint document library.

        Parameters
        ----------
        path : str
            The path of the directory to delete, relative to the site as a whole. File paths are UNIX-like.

        Raises
        ------
        FileExistsError
            If the folder already exists.
        FileNotFoundError
            If the document library does not exist.
        Exception
            If an API error has occured that is not otherwise caught.
        NotADirectoryError
            If the file referenced is not a directory.
        """

        path_list = path.split("/")
        path_list = list(filter(None, path_list))

        if path_list[0] not in self.libraries:
            raise FileNotFoundError(f"Document Library {path_list[0]} not found.")

        if path_list[0] is path_list[-1]:
            raise Exception("Will not delete document library.")

        if path_list[0] in self.list_files("/".join(path_list[:-1])):
            raise NotADirectoryError()
        elif self.listdir(path):
            raise OSError("Directory is not empty.")

        api_url = f"{self._site_url}/_api/web/GetFolderByServerRelativeUrl('{path}')"

        headers = {"X-HTTP-Method": "DELETE"}
        headers.update(self._header)

        request = requests.post(url=api_url, headers=headers)

        if len(request.content) > 0:
            request = json.loads(request.content)
        if "error" in request:
            error_code = request["error"]["code"]
            raise Exception(request["error"]["message"]["value"])

    def remove(self, path: str) -> None:
        """Delete a file on a SharePoint document library.

        Parameters
        ----------
        path : str
            The path of the file to delete, relative to the site as a whole. File paths are UNIX-like.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        Exception
            If an API error has occured that is not otherwise caught.
        NotADirectoryError
            If the file referenced is not a directory.
        """

        path_list = path.split("/")
        path_list = list(filter(None, path_list))
        directory_path = "/".join(path_list[:-1])
        file_name = path_list[-1]

        if path_list[0] not in self.libraries:
            raise FileNotFoundError(f"Document Library {path_list[0]} not found.")

        if path_list[0] is path_list[-1]:
            raise Exception("Will not delete document library.")

        if file_name not in self.list_files(directory_path):
            raise FileNotFoundError()

        api_url = f"{self._site_url}/_api/web/GetFolderByServerRelativeUrl('{directory_path}')/Files('{file_name}')"

        headers = {"X-HTTP-Method": "DELETE"}

        headers.update(self._header)

        request = requests.post(url=api_url, headers=headers)

        if len(request.content) > 0:
            request = json.loads(request.content)
        if "error" in request:
            error_code = request["error"]["code"]
            raise Exception(request["error"]["message"]["value"])

    def open(self, filepath: str, mode: str = "r", checkout: bool = False):
        """Open a file from a SharePoint document library and return a file-like object.

        Parameters
        ----------
        filepath : str
            The path of the file to return, relative to the site as a whole. File paths are UNIX-like.
        checkout : bool
            If True, the file will be checked out of Sharepoint and locked.
        mode : str
            File mode, append mode is not supported. Default is "r+b".

        Returns
        ------
        SharepointFile
            File-like object.
        """
        mode = mode.replace("t", "")
        if mode not in ("w", "w+", "wb", "w+b", "r", "r+", "rb", "r+b"):
            raise ValueError(
                f"Invalid mode. Supported modes are 'r', 'r+', 'w', 'w+', 'rb', 'wb', 'r+b', 'w+b'."
            )
        if "a" in mode:
            raise NotImplementedError()
        elif "b" in mode:
            return sharepoint_file.SharepointBytesFile(
                header=self._header,
                sharepoint_site=self._site_url,
                filepath=filepath,
                checkout=checkout,
                mode=mode,
            )
        else:
            return sharepoint_file.SharepointTextFile(
                header=self._header,
                sharepoint_site=self._site_url,
                filepath=filepath,
                checkout=checkout,
                mode=mode,
            )

    @property
    def name(self) -> str:
        api_url = f"{self._site_url}/_api/web/title"
        request = json.loads(requests.get(api_url, headers=self._header).content)
        return request["d"]["Title"]

    @property
    def description(self) -> str:
        api_url = f"{self._site_url}/_api/web/description"
        request = json.loads(requests.get(api_url, headers=self._header).content)
        return request["d"]["Description"]

    @property
    def subsites(self) -> dict:
        api_url = f"{self._site_url}/_api/web/webs/?$select=title,Url"
        request = requests.get(api_url, headers=self._header).text
        request = json.loads(request)
        request = request["d"]["results"]
        sites = {site['Title']: site['Url'] for site in request}
        return sites
    
    def get_subsite(self, site_name: str) -> Self:
        """Grab a subsite.

        Parameters
        ----------
        site_name : str
            The user-facing name of a SharePoint subsite

        Raises
        ------
        KeyError
            If the subsite does not exist.

        Returns
        ------
        SharepointSite
        """

        site_url = None
        subsites = self.subsites
        if site_name in subsites.keys():
            site_url = subsites[site_name]
        else:
            raise KeyError("Site not found.")

        return SharepointSite(site_url, self.base_url, self._header)