import re

with open('./08_SELF_IMPROVEMENT/test_suite.py', 'r') as f:
    content = f.read()

# Replace the boundary error test
old_boundary = """        boundary_refused = False
        try:
            si_mod._assert_inside_workspace(Path(r'E:\\CLAUDE\\MINTE\\x.md'))
        except BoundaryError:
            boundary_refused = True
        result.assert_true(boundary_refused, 'a write outside the boundary is refused')"""

new_boundary = """        from pathlib import Path
        boundary_refused = False
        try:
            si_mod._assert_inside_workspace(Path(r'E:\\CLAUDE\\MINTE\\x.md'))
        except BoundaryError:
            boundary_refused = True
        result.assert_true(boundary_refused, 'a write outside the boundary is refused')"""

content = content.replace(old_boundary, new_boundary)

with open('./08_SELF_IMPROVEMENT/test_suite.py', 'w') as f:
    f.write(content)
