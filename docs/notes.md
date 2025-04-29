# Handling Images
Endpoint is
https://url/VisureAuthoring8/api/v1/element/{id}/uploadImage

Upload the image, the return is then in the form:
{
    "link": "https://url/VisureAuthoring8/session/M45IiS16c0CsC5eLh9N3Xw/500/image.png"
}

The UI then calls autosave

Then update the description:
https://url/VisureAuthoring8/api/v1/element/{id}/description

{ description : "<p align="justify" style="margin-top:0; margin-bottom:0; line-height: 12pt; min-height: 12pt;"><span dir="ltr" style="font-family:Calibri; font-size:11.0pt; color:#010101;"><em>&lt;Don&rsquo;t really say &ldquo;System Feature 1.&rdquo; State the feature name in just a few words.&gt;</em></span></p><p align="justify" style="margin-top:0; margin-bottom:0; line-height: 12pt; min-height: 12pt;"><span dir="ltr" style="font-family:Calibri; font-size:11.0pt; color:#010101;"><em><img src="https://URL/VisureAuthoring8/session/M45IiS16c0CsC5eLh9N3Xw/500/image.png" style="width: 300px;" class="fr-fic fr-dib"></em></span><br></p>"}

Then checkin

# Handling in-line links to other items
Add this to the description:
<a href="#BM_VR_000547_-000001" target="_blank" rel="nofollow noopener noreferrer">SYSREQ-1 (Code)</a>
Element ID in this case is 547
---01 is code
---02 is name
---03 is description


href=\"#BM_VR_000546_-000518\" target=\"_blank\" rel=\"nofollow noopener noreferrer\">546 (Verification Method)</a>

# Getting elements
It appears that you can get at elements without needing a spec by passing -1 as the spec id

This is the UI's go-to request for a particular item:
```python
import requests

url = "https://company.visurecloud.com/VisureAuthoring8/api/v1/specification/-1/elements/byids"

querystring = {"includeAttributes":"true","textToSearch":"","ignoreActiveFilters":"true","includeLinkedItems":"true"}

payload = {"elementIDs": [532]}
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "authorization": "Bearer XXXX",
    "content-type": "application/json",
    "Cookie": "https%3A%2F%2Fcompany.visurecloud.com%2FVisureAuthoring8%2F_visure-tabs-number=1",
    "ngsw-bypass": "",
    "origin": "https://company.visurecloud.com",
    "priority": "u=1, i",
    "referer": "https://company.visurecloud.com/VisureAuthoring8/specification",
    "sec-ch-ua": ""Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": ""Windows"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0"
}

response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

print(response.text)
```


# Linking to other items in-line
Use case: system parameters

Update the description:
<a href=\"#BM_VR_003763_-000002\" target=\"_blank\" rel=\"nofollow noopener noreferrer\">SWSR_0010 (Name)&nbsp;</a>

3763 - spec id
SWSR_0010 (Name) - Text to display


# Creating elements

Payload is 
{
  "specificationID": 104, // Specification to create in
  "selectedElement": 222, // Heading? idrk. Set to spec ID to make it a top level item
  "asChildren": false,
  "numberOfElements": 1
}

Making something a parent puts it under the numbering, e.g.

1.1 Example A
1.2 Example B (created not as children, selected element is example A)

vs

1.1 Example A
1.1.1 Example B (created as children, selected element is example A)

# Changing attributes
If the particular id is known
{
  "parentId": 4027,
  "id": 479, // element ID
  "baseType": "ENUMERATED",
  "isMultivalued": false,
  "values": [
    "Heading"
  ]
}

# Linking
endpoint is 
https://company.visurecloud.com/VisureAuthoring8/api/v1/elements/relationship/{first item}/{second item}

link is FROM first item TO second item, i.e. first item is upstream

returns list of acceptable links in the form of:
[{"sourceID":532,"targetID":533,"id":432,"name":"Satisfied by"}]

Actually create the link with
https://company.visurecloud.com/VisureAuthoring8/api/v1/elements/relationship/create

[
    {
    "id": 432,
    "sourceID": 4033,
    "targetID": 4034,
    "isSuspect": false,
    "projectID": 2,
    "targetProjectID": 2,
    "motiveName": "Satisfied by"
    },
    ...
]

# Modifying attributes
POST to https://company.visurecloud.com/VisureAuthoring8/api/v1/element/attribute/values
Payload is 
{
  "parentId": 4037, # Item ID
  "id": 479, # Attribute ID
  "baseType": "ENUMERATED", # stored in visure\primatives\enums.py, or can be any string for custom type
  "isMultivalued": false,
  "values": [
    "Heading"
  ]
}