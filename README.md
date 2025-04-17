# visure
This is a library to interact with the Visure REST API from Python.

## Usage
```python
from pprint import pprint
from visure.visure import Visure

obj = Visure("https://mycompany.visurecloud.com", "myusername", "mypassword")
pprint(obj.projects) # We can also do obj.get_projects(), but we get the data "for free" alongside the authentication step 
```

## Contributing
Contributions welcome!
You can access your API with `https://<your_instance>.com/visureauthoring8/swagger/index.html`