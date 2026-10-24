🎯 **What:** Added a missing error test for `_validate` URL in `web_tools_server.py`.

📊 **Coverage:** Now tests valid HTTP/HTTPS URLs as well as invalid schemas (FTP) and badly formatted URLs without a host to ensure the function properly catches and returns errors/raises ToolError as designed.

✨ **Result:** Test suite coverage has been improved with a new `test_web_tools_validate_url` function to safely assert validation logic using AST execution logic to avoid polluting test state.
