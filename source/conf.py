# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'test-project'
copyright = '2026, Bruno Benno Reichert'
author = 'Bruno Benno Reichert'
release = '0.0.0.0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os
import sys

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = []

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Course 2', 'E4 - Automatic doc tools')))


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

# -- Options for LaTeX output -------------------------------------------------

latex_elements = {
    # 'oneside' prevents blank pages between chapters
    # 'openany' allows new chapters to start on even or odd pages
    'extraclassoptions': 'oneside,openany',
}