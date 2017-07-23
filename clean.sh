#!/bin/bash

find_cmd="-print"
function find_files {
    find -E . -type f -regex "(.*\.(pyc|s|out))|(.*/parsetab\.py)|(.*/parser\.out)" $find_cmd
}

echo "Remove the following files:"
find_files

find_cmd="-delete"
find_files
