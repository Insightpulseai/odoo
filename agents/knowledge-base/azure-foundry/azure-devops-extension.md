# Develop a web extension - Azure DevOps

## Overview
Use extensions to enhance Azure DevOps with new web experiences, dashboard widgets, build tasks, and more. You can develop extensions using standard technologies like HTML, JavaScript, and CSS.

### Prerequisites
- Node.js
- `npm install -g tfx-cli`

## Create a directory and manifest

1. Create a directory to hold the files needed for your extension:
   ```bash
   mkdir my-first-extension
   ```
2. Initialize a new npm package manifest:
   ```bash
   npm init -y
   ```
3. Install the SDK:
   ```bash
   npm install azure-devops-extension-sdk --save
   ```

## Extension Manifest (vss-extension.json)
Create `vss-extension.json` at the root:

```json
{
    "manifestVersion": 1,
    "id": "my-first-extension",
    "publisher": "",
    "version": "1.0.0",
    "name": "My First Extension",
    "description": "A sample Visual Studio Services extension",
    "public": false,
    "categories": ["Azure Repos"],
    "targets": [
        {
            "id": "Microsoft.VisualStudio.Services"
        }
    ],
    "contributions": [
        {
            "id": "my-hub",
            "type": "ms.vss-web.hub",
            "targets": [
                "ms.vss-code-web.code-hub-group"
            ],
            "properties": {
                "name": "My Hub",
                "uri": "my-hub.html"
            }
        }
    ],
    "files": [
        {
            "path": "my-hub.html",
            "addressable": true
        },
        {
            "path": "node_modules/azure-devops-extension-sdk",
            "addressable": true,
            "packagePath": "lib"
        }
    ]
}
```

*Note: Keep `public: false` during development.*

## Hub Page (my-hub.html)
```html
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.6/require.min.js"></script>
    <script>
        window.requirejs.config({
            enforceDefine: true,
            paths: {
                'SDK': './lib/SDK.min'
            }
        });
        window.requirejs(['SDK'], function (SDK) {
            if (typeof SDK !== 'undefined') {
                console.log("SDK is defined. Trying to initialize...");
                SDK.init();
                SDK.ready().then(() => {
                    console.log("SDK is ready");
                    document.getElementById("name").innerText = SDK.getUser().displayName;
                });
            } else {
                console.log('SDK is not defined');
            }
        });
    </script>
    <style>
        body {
            background-color: rgb(0, 67, 117);
            color: white;
            margin: 10px;    
            font-family: "Segoe UI VSS (Regular)","-apple-system",BlinkMacSystemFont,"Segoe UI",sans-serif;
        }
    </style>
</head>
<body>        
    <h1>Hello, <span id="name"></span></h1>
</body>
</html>
```

## Next steps
Package and publish your extension using `tfx-cli`.
