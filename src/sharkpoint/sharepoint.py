import requests
import json
from . import sharepoint_site
from azure.core.credentials import TokenCredential


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
    site_names : str
        a list of all user-facing site names in SharePoint
    sites : dict
        a dictionary of all sites in SharePoint, the key is the user-facing name and the value is the URL
    base_url : str
        the URL of the SharePoint instance

    Methods
    -------
    get_site(site_name)
        Returns a SharepointSite object for a specific SharePoint site
    create_site(site_name, path, owner, description, web_template, lcid, site_design_id)
        Creates a new site and returns a SharepointSite object for the site
    """

    def __init__(
        self,
        sharepoint_url: str,
        azure_identity: TokenCredential,
    ) -> None:
        self.base_url = sharepoint_url
        self._scope = f"{self.base_url}/.default"
        self._identity = azure_identity

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

    @property
    def sites(self) -> dict:
        api_url = f"{self.base_url}_api/search/query?querytext='contentclass:STS_Site'"
        request = requests.get(api_url, headers=self._header).text
        request = json.loads(request)
        # fmt: off
        request = request["d"]["query"]["PrimaryQueryResult"]["RelevantResults"]["Table"]["Rows"]["results"]
        # fmt: on
        # By G-d Almighty this looks ugly, but this is the easiest way to parse the table for what I need
        sites_dict = {site["Cells"]["results"][2]["Value"]: site["Cells"]["results"][5]["Value"] for site in request}
        return sites_dict

    def get_site(self, site_name: str) -> sharepoint_site.SharepointSite:
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
        site_url = None
        sites = self.sites
        if site_name in sites.keys():
            site_url = sites[site_name]
        else:
            raise KeyError("Site not found.")

        return sharepoint_site.SharepointSite(site_url, self.base_url, self._header)

    def create_site(
        self,
        site_name: str,
        path: str,
        owner: str,
        description: str,
        web_template: str = "sts#3",
        lcid: int = 1033,
        site_design_id: str = "00000000-0000-0000-0000-000000000000",
    ) -> sharepoint_site.SharepointSite:
        api_url = f"{self.base_url}/_api/SPSiteManager/create"
        request = {
            "request": {
                "Title": site_name,
                "Url": f"{self.base_url}/sites/{path}",
                "Lcid": str(lcid),
                "ShareByEmailEnabled": "false",
                "Description": description,
                "WebTemplate": web_template,
                "SiteDesignId": site_design_id,
                "Owner": owner,
            }
        }
        request_return = requests.post(
            api_url, data=json.dumps(request), headers=self._header
        )
        request_return = json.loads(request_return.content)
        if request_return["d"]["Create"]["SiteStatus"] == 2:
            return sharepoint_site.SharepointSite(request_return["d"]["Create"]["SiteUrl"], self.base_url, self._header)
        else:
            raise Exception(request_return["d"]["Create"]["SiteStatus"])
