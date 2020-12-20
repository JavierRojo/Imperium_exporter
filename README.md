![](https://img.shields.io/badge/Blender%20version-2.8x-orange?style=for-the-badge&logo=blender&logoColor=white)
![](https://img.shields.io/github/v/tag/JavierRojo/Imperium_exporter?color=green&label=Add-on%20version&logo=python&logoColor=white&style=for-the-badge)

# Imperium exporter
A [Blender](https://www.blender.org/) renderer for Imperium textures. The purpose of this add-on is the automation of the process of creating textures for mods of this wonderful gane, The whole project is divided into 3 parts:

* [x] T1: Render a series of sprites of an animated figure in PNG format. This sprites will be rendered into a a custom folder.
* [x] T2: Transform in [Octave](https://www.gnu.org/software/octave/) all the sprites in a folder into a format compatible with the game.
* [ ] T3: Transfer T2 functinallity into Blender, so only one click is needed.

The third part will be delayed until more capabilities are implemented. A TODO list can be found below.

## TODO list
* [ ] Finish T2 (documentation and functions).
* [ ] Better document the tool.
* [x] Avoid double for loops.
* [ ] Implement shadow textures.
* [x] Implement level colors.
* [ ] Implement player colors.
* [ ] Implement building textures.
* [ ] Implement GUI textures.
* [ ] Move everything to python (Blender) in T3.

## How to install it
To install imperium renderer just download or clone this repository and then go to Blender. In _edit > preferences > add-ons_ select 'install from file' and then navigate to this recently downloaded folder and select the imperium\_renderer.py file.

## How to use it
### Blender
First, create the model of your asset (unit, building, etc.) and animate it if necessary. Then, create a default camera in the addon panel or modify a camera you have selected. This should give you an imperium-like view of your model. Then adjust the resolution and the number of frames for that animation. Don't forget to extend the start and end frames so the whole animation is included.

Create an empty object and make the armature/mesh child of this empty by selecting the armature, then the empty (holding shift) and pressing 'P' (parent). With the object picker select the empty and finally select the output path. Once these steps are done you can press the 'Render' button and the sprites will be rendered into the output folder.

### Octave
Now the `confiuration.cfg` file must be properly filled with the spritesheet details. Once this is done the `imperium_assembler.m` file can be executed from Octave. Although you can use the console version, for new people I recommend the more user-friendly GUI version. Select the working directory on the top drop-down menu and type _imperium\_assembler_ in the console (or push the play button). In the output folder specified in the configuration a new bmp image will appear. This texture is ready to be converted to mmp and compressed into the package used by the game. 

## More info
* When this tool is finished I will update the [wiki](https://github.com/JavierRojo/Imperium_exporter/wiki).
* The result of this add-on can be found in this [video](https://youtu.be/MGJLMHRm75E).
* More information can be found in my [Youtube channel](https://www.youtube.com/playlist?list=PL_zV6BZZ-V3c3P5ECvt4QKXoIlzdFlKu2).
