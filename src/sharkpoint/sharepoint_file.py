import io
from types import TracebackType
import requests


class SharepointBytesFile(io.BytesIO):
    """
    SharepointFile(header, sharepoint_site, filepath, checkout)

    A file-like class used to represent a SharePoint file using the SharePoint REST API v1.

    Methods
    -------
    check_back_in()
        Manually check a file into SharePoint and remove the file lock
    """

    def __init__(
        self,
        header,
        sharepoint_site: str,
        filepath: str,
        checkout: bool,
        mode: str = "r+b",
    ):
        self._header = header
        self._site = sharepoint_site
        self._path, self._filename = self._get_filepath(filepath)
        self._checkout = checkout
        self._mode = mode

        if self._mode not in ("rb", "wb", "r+b", "w+b"):
            raise ValueError(
                "Invalid mode. Supported modes are 'rb', 'wb', 'r+b', 'w+b'."
            )

        if self._mode in ("wb", "w+b"):
            super().__init__()
        else:
            file_content = self._get_file()
            super().__init__(file_content)

    def _get_filepath(self, path: str):
        path = path.split("/")
        return "/".join(path[:-1]), path[-1]

    def _get_file(self):
        if self._checkout:
            api_url = f"{self._site}/_api/web/GetFolderByServerRelativeUrl('{self._path}')/Files('{self._filename}')/CheckOut()"
            requests.post(api_url, headers=self._header)

        api_url = f"{self._site}/_api/web/GetFolderByServerRelativeUrl('{self._path}')/Files('{self._filename}')/$value"
        file = requests.get(api_url, headers=self._header)
        return file.content

    def write(self, data):
        if self._mode not in ("wb", "w+b", "r+b"):
            raise IOError("File not open in write mode.")
        super().write(data)

    def flush(self):
        if self._mode not in ("wb", "w+b", "r+b"):
            raise IOError("File not open in write mode.")
        super().flush()
        api_url = f"{self._site}/_api/web/GetFolderByServerRelativeUrl('{self._path}')/Files/add(url='{self._filename}', overwrite=true)"

        file_size = len(super().getvalue())
        post_request = {
            "Content-Length": str(file_size),
            "X-HTTP-Method": "PUT",
        }

        post_request.update(self._header)
        file_content = super().getvalue()
        requests.put(api_url, data=file_content, headers=post_request)

    def read(self, size=-1):
        if self._mode not in ("rb", "r+b", "w+b"):
            raise IOError("File not open in read mode.")
        return super().read(size)

    def check_back_in(self):
        if self._checkout:
            api_url = f"{self._site}/_api/web/GetFolderByServerRelativeUrl('{self._path}')/Files('{self._filename}')/CheckIn(comment='Comment',checkintype=0)"
            requests.post(api_url, headers=self._header)

    def close(self):
        self.check_back_in()
        if self._mode in ("wb", "w+b", "r+b"):
            self.flush()
        super().close()

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        super().__exit__(exc_type, exc_val, exc_tb)


class SharepointTextFile(io.StringIO):
    """
    SharepointFile(header, sharepoint_site, filepath, checkout)

    A file-like class used to represent a SharePoint file using the SharePoint REST API v1.

    Methods
    -------
    check_back_in()
        Manually check a file into SharePoint and remove the file lock
    """

    def __init__(
        self,
        header,
        sharepoint_site: str,
        filepath: str,
        checkout: bool,
        mode: str = "r",
    ):
        self._header = header
        self._site = sharepoint_site
        self._path, self._filename = self._get_filepath(filepath)
        self._checkout = checkout
        self._mode = mode

        if self._mode not in ("r", "w", "r+", "w+"):
            raise ValueError("Invalid mode. Supported modes are 'r', 'w', 'r+', 'w+'.")

        if self._mode in ("w", "w+"):
            super().__init__()
        else:
            file_content = self._get_file().decode()
            super().__init__(file_content)

    def _get_filepath(self, path: str):
        path = path.split("/")
        return "/".join(path[:-1]), path[-1]

    def _get_file(self):
        if self._checkout:
            api_url = f"{self._site}/_api/web/GetFolderByServerRelativeUrl('{self._path}')/Files('{self._filename}')/CheckOut()"
            requests.post(api_url, headers=self._header)

        api_url = f"{self._site}/_api/web/GetFolderByServerRelativeUrl('{self._path}')/Files('{self._filename}')/$value"
        file = requests.get(api_url, headers=self._header)
        return file.content

    def write(self, data):
        if self._mode not in ("w", "w+", "r+"):
            raise IOError("File not open in write mode.")
        super().write(data)

    def flush(self):
        if self._mode not in ("w", "w+", "r+"):
            raise IOError("File not open in write mode.")
        super().flush()
        api_url = f"{self._site}/_api/web/GetFolderByServerRelativeUrl('{self._path}')/Files/add(url='{self._filename}', overwrite=true)"

        file_size = len(super().getvalue().encode())
        post_request = {
            "Content-Length": str(file_size),
            "X-HTTP-Method": "PUT",
        }

        post_request.update(self._header)
        file_content = super().getvalue().encode()
        requests.put(api_url, data=file_content, headers=post_request)

    def read(self, size=-1):
        if self._mode not in ("r", "r+", "w+"):
            raise IOError("File not open in read mode.")
        return super().read(size)

    def check_back_in(self):
        if self._checkout:
            api_url = f"{self._site}/_api/web/GetFolderByServerRelativeUrl('{self._path}')/Files('{self._filename}')/CheckIn(comment='Comment',checkintype=0)"
            requests.post(api_url, headers=self._header)

    def close(self):
        self.check_back_in()
        if self._mode in ("w", "w+", "r+"):
            self.flush()
        super().close()

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        super().__exit__(exc_type, exc_val, exc_tb)