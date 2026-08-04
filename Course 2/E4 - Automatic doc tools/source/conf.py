import os
import sys

# New relative path: Just go up one level to reach the E4 directory!
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

extensions = [
    'sphinx.ext.autodoc'
]

# (Optional) Retain our settings from yesterday to prevent blank pages
latex_elements = {
    'extraclassoptions': 'oneside,openany',
}