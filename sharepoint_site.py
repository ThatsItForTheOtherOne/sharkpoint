import json
import requests
import sharepoint_file


class SharepointSite:
    """
    SharePointSite(sharepoint_site_name, sharepoint_site_url, sharepoint_base_url, header)

    A class used to represent a SharePoint site using the SharePoint REST API v1. 
    ...
    
    Parameters
    ----------
    sharepoint_site_name : str
        The user-facing name of the Sharepoint site
    sharepoint_site_url : str 
        The URL of the Sharepoint site
    sharepoint_base_url : str
        The URL of the Sharepoint instance
    header : dict
        The header for requests made to the API containing the Bearer token
    
    Attributes
    ----------
    site_name : str
        The user-facing name of the Sharepoint site

    Methods
    -------
    listdir(path)
        Returns a list of directories in a document library
    mkdir(path)
        Creates a new directory in a document library
    open(path, checkout = False)
        Downloads a file from a document library and returns a SharepointFile object
    """

    def __init__(
        self,
        sharepoint_site_name: str,
        sharepoint_site_url: str,
        sharepoint_base_url: str,
        header,
    ) -> None:
        self.site_name = sharepoint_site_name
        self._site_url = sharepoint_site_url
        self._base_url = sharepoint_base_url
        self._header = header
        self._libraries = self._get_libraries()

    def _get_libraries(self):
        api_url = f"{self._site_url}/_api/web/lists?$select=Title,ServerRelativeUrl&$filter=BaseTemplate eq 101 and hidden eq false&$expand=RootFolder"
        request = requests.get(api_url, headers=self._header)
        request = json.loads(request.content)

        request = request["d"]["results"]
        libraries = {}

        for library in request:
            library_name = library["RootFolder"]["Name"]
            library_path = library["RootFolder"]["ServerRelativeUrl"]
            libraries[library_name] = library_path

        return libraries

    def listdir(self, path: str):
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
        """

        path_list = path.split("/")
        path_list = list(filter(None, path_list))

        if path_list[0] not in self._libraries:
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
        directory_list = []

        for file in files:
            directory_list.append(file["Name"])
        for folder in folders:
            directory_list.append(folder["Name"])

        return directory_list

    def mkdir(self, path: str):
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

        if path_list[0] not in self._libraries:
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

    def open(self, filepath: str, checkout: bool = False):
        """Open a file from a SharePoint document library and return a file-like object.

        Parameters
        ----------
        filepath : str
            The path of the file to return, relative to the site as a whole. File paths are UNIX-like.
        checkout : bool
            If True, the file will be checked out of Sharepoint and locked.
        Returns
        ------
        SharepointFile
            File-like object.
        """

        return sharepoint_file.SharepointFile(
            header=self._header,
            sharepoint_site=self._site_url,
            filepath=filepath,
            checkout=checkout,
        )
