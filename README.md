# Overview
A command line utility for combining two DCS World missions together.

# Features
* Currently this tool does one thing:  It moves all the client flights from one mission into another.
  * This can be useful for mission devs who add lots of client flights to their missions.  You can work on the static groups/air defences or whatever, then bring in all the client flights afterward.


# Installation and Usage
## Installation
pip install the pypi package

`pip install dcs-mizmerge`

Until the pypi wheel for pydcs is updated to 0.13.0, you may need to manually install it using this command

`pip install -e git+https://github.com/pydcs/dcs@fac1bd084f22150acfde3bff220f8e69487048d1#egg=pydcs`

## Usage

`dcs-mizmerge "C:\PathToMissionWithClientFlightsHere.miz" "C:\PathToMissionYouWantToMergeClientFlightsIntoHere.miz"`

By default, the merged mission file will be saved at the path of the second argument, with `_merged` appended to the end of the filename.  You can change the output file location with the `--output` option.

`dcs-mizmerge "C:\PathToMissionWithClientFlightsHere.miz" "C:\PathToMissionYouWantToMergeClientFlightsIntoHere.miz" --output "C:\SomeNewPathHere"`


# Thanks
Only possible due to the work of rp- and the other devs at [!pydcs](https://github.com/pydcs/dcs).
Mod support was copied from [!DCS Liberation](https://github.com/dcs-liberation/dcs_liberation), thanks to everyone there.
