# DocuSplit

Converts XML data to JSON and then either dumps the data or performs an analysis on the data struction.

Analyze a file:
````
bin/docmgr --file ~/Downloads/DATA_012345.xml -v > ~/DATA_012345.dat
````

Dump to JSON:
````
bin/docmgr --file ~/Downloads/DATA_012345.xml --dump > ~/DATA_012345.json
````

Start at key depth 2 (skip first 2 nested keys before processing the data):
````
bin/docmgr --file ~/Downloads/DATA_012345.xml --dump --depth 2 > ~/DATA_012345.json
````

Dump a list located in a nested key where each list element is its own file:
```
bin/docmgr --file ~/Downloads/DATA_012345.xml --dump --split --dir ~/data --base DATA_012345 --key data.sub-data.target --list --depth 2
```

Same example as above, but denote that there is am array element where you want to traverse below the array to find the target key:
```
bin/docmgr --file ~/Downloads/DATA_012345.xml --dump --split --dir ~/data --base DATA_012345 --key 'data.sub-data.[].more-data.target' --list --depth 2
```
