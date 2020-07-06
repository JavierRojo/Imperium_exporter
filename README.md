![](https://img.shields.io/badge/Blender%20version-2.8x-orange?style=for-the-badge&logo=blender&logoColor=white)
![](https://img.shields.io/github/v/tag/JavierRojo/Imperium_exporter?color=green&label=Add-on%20version&logo=python&logoColor=white&style=for-the-badge)

# Imperium exporter
A [Blender](https://www.blender.org/) renderer for Imperium textures. The purpose of this add-on is the automation of the process of creating textures for mods of this wonderful gane, The whole project is divided into 3 parts:

* [x] T1: Render a series of sprites of an animated figure in PNG format. This sprites will be rendered into a a custom folder.
* [ ] T2: Transform in [Octave](https://www.gnu.org/software/octave/) all the sprites in a folder into a format compatible with the game.
* [ ] T3: Transfer T2 functinallity into Blender, so only one click is needed.

## How to install it
To install imperium renderer just download or clone this repository and then go to Blender. In _edit > preferences > add-ons_ select 'install from file' and then navigate to this recently downloaded folder and select the imperium\_renderer.py file.

## How to use it
First, create the model of your asset (unit, building, etc.) and animate it if necessary. Then, create a default camera in the addon panel or modify a camera you have selected. This should give you an imperium-like view of your model. Then adjust the resolution and the number of frames for that animation. Don't forget to extend the start and end frames so the whole animation is included.

Create an empty object and make the armature/mesh child of this empty by selecting the armature, then the empty (holding shift) and pressing 'P' (parent). With the object picker select the empty and finally select the output path. Once these steps are done you can press the 'Render' button and the sprites will be rendered into the output folder.

## More info
When this tool is finished I will update the [wiki](https://github.com/JavierRojo/Imperium_exporter/wiki).
More information can be found in my [Youtube channel](https://www.youtube.com/playlist?list=PL_zV6BZZ-V3c3P5ECvt4QKXoIlzdFlKu2).
