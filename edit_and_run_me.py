# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 18:14:01 2020
Author : Teskann

Edit and run this file to run Docapy on your project !
"""

if __name__ == "__main__":
    
    # Import Docapy core
    from docapy import html_for_project
    
    # Project Name (edit it)
    project_name = "Your Project Name Here"
    
    # Project Path
    project_path = "Your project path here (absolute path recommended)"
    
    # Repository Link
    repo_link = "Link of the repository of this project goes here"
    
    # Accent color.
    # This variable can be :
    # - "blue"
    # - "cyan"
    # - "red"
    # - "green"
    # - "orange"
    # - "purple"
    # - "#XXXXXX" where XXXXXX is a hexadecimal color value (custom)
    color = "Accent color of the generated website goes here"
    
    # Running Docapy (do not edit this part)
    html_for_project(project_path,
                 project_name,
                 repo_link,
                 color)