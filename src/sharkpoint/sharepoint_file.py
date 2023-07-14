import io
from types import TracebackType
import requests


class SharepointFile(io.BytesIO):
    """
    SharepointFile(header, sharepoint_site, filepath, checkout)

    A file-like class used to represent a SharePoint file using the SharePoint REST API v1.

    Methods
    -------
    check_back_in()
        Manually check a file into SharePoint and remove the file lock
    """

    def __init__(self, header, sharepoint_site: str, filepath: str, checkout: bool):
        self._header = header
        self._site = sharepoint_site
        self._path, self._filename = self._get_filepath(filepath)
        self._checkout = checkout
        super().__init__(self._get_file())

    def _get_filepath(str, path: str):
        path = path.split("/")
        return "/".join(path[:-1]), path[-1]

    def _get_file(self):
        if self._checkout:
            api_url = f"{self._site}/_api/web/GetFolderByServerRelativeUrl('{self._path}')/Files('{self._filename}')/CheckOut()"
            requests.post(api_url, headers=self._header)

        api_url = f"{self._site}/_api/web/GetFolderByServerRelativeUrl('{self._path}')/Files('{self._filename}')/$value"
        file = requests.get(api_url, headers=self._header)
        return file.content

    def flush(self):
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

    def check_back_in(self):
        if self._checkout:
            api_url = f"{self._site}/_api/web/GetFolderByServerRelativeUrl('{self._path}')/Files('{self._filename}')/CheckIn(comment='Comment',checkintype=0)"
            requests.post(api_url, headers=self._header)

    def close(self) -> None:
        self.check_back_in()
        return super().close()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.check_back_in()
        return super().__exit__(exc_type, exc_val, exc_tb)
