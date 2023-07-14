import azure.identity
import requests
import json
from . import sharepoint_site
import azure.core.credentials


class SharePoint:
    """
    A class used to represent an organization's SharePoint instance using the SharePoint REST API v1.
    ...

    Parameters
    ----------
    base_url : str
        The URL of a Sharepoint instance, ex. contoso.sharepoint.com
    azure_identity : TokenCredential
        An azure-identity token credential.

    Attributes
    ----------
    sites : dict
        a dictionary of all sites in SharePoint, the key is the user-facing name and the value is the URL
    base_url : str
        the URL of the SharePoint instance

    Methods
    -------
    get_site(site_name)
        Returns a SharepointSite object for a specific SharePoint site
    """

    def __init__(
        self,
        sharepoint_url: str,
        azure_identity: azure.core.credentials.TokenCredential,
    ) -> None:
        self.base_url = sharepoint_url
        self._scope = f"{self.base_url}/.default"
        self._identity = azure_identity
        self.sites = self._initalize_sites()

    @property
    def _token(self):
        return self._identity.get_token(self._scope)

    @property
    def _header(self):
        return {
            "Authorization": f"Bearer {self._token.token}",
            "Accept": "application/json;odata=verbose",
            "Content-Type": "application/json;odata=verbose",
        }

    def _initalize_sites(self):
        api_url = f"{self.base_url}/_api/search/query?querytext='contentclass:STS_Site contentclass:STS_Web'&selectproperties='Title,Path'"
        request = requests.get(api_url, headers=self._header).text
        request = json.loads(request)
        # fmt: off
        request = request["d"]["query"]["PrimaryQueryResult"]["RelevantResults"]["Table"]["Rows"]["results"]
        # fmt: on

        sites = []
        for x in request:
            site_dict = {
                "Site Name": x["Cells"]["results"][0]["Value"],
                "Site Path": x["Cells"]["results"][1]["Value"],
            }
            sites.append(site_dict)
        return sites

    def get_site(self, site_name):
        """
        Parameters
        ----------
        site_name : str
            The user-facing name of a SharePoint site

        Raises
        ------
        KeyError
            If the subsite does not exist

        """

        site_url = next(
            (item for item in self.sites if item["Site Name"] == site_name), None
        )
        if site_url is None:
            raise KeyError("Site not found.")
        else:
            site_url = site_url["Site Path"]
        return sharepoint_site.SharepointSite(site_url, self.base_url, self._header)
