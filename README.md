# SharkPoint
A small library for interacting with SharePoint document libaries (and hopefully more!)

# Usage

```
import sharkpoint
import azure.identity

ident = azure.identity.AzureDefaultCredential()
sharepoint_instance = sharkpoint.Sharepoint("contoso.sharepoint.com", ident)

site = sharkpoint.get_site("spam")
site.listdir("Shared Documents/")

file = site.open("Shared Documents/eggs.txt")
file.write("foo")
file.close()
```

# Why SharkPoint?
I couldn't think of anything else
