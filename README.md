# HairWorks-Exporter-For-Blender
A Blender Addon that will allow you to export a Blender hair particle system to an application that supports the import of HairWorks .apx files.

HOW TO INSTALL THE ADDON

1. Navigate to the directory blender was installed in.
2. Navigate to the following folder InstallDir\VersionNumber\scripts\addons. For example: C:\Blender\2.91\scripts\addons
3. Paste the entire io_export_apx folder in that directory.
4. Open Blender.
5. Open File->User Preferences.
6. Under the Addons tab search for HairWorks.
7. Tick the box to enable the addon.
8. Under File->Export "HairWorks (.apx)" should now be visible.

REQUIREMENTS TO EXPORT

1. Have a mesh selected.
2. Triangulate faces.
3. UV unwrap mesh.
4. Skin to armature.
5. Hair particle system should be the first particle system.


LIMITATIONS AND PROBLEMS

1. All vertices of growth mesh must emit a hair.
2. No more or less hairs than vertices.
3. Addon still slow and unoptimized (could freeze or crash with large amounts of hair).
4. Buggy when advanced animations or rigs applied.
5. Only one hair particle system exports at the moment.

RELAVANT LINKS

HAIRWORKS VIEWER :

https://developer.nvidia.com/gameworksdownload
click on HairWorks 1.1.1

UNREAL ENGINE HAIRWORKS BRANCH:

https://github.com/NvPhysX/UnrealEngine/tree/HairWorks

UNREAL ENGINE MERGED GAMEWORKS BRANCH:

https://github.com/GalaxyMan2015/UnrealEngine/tree/4.9.2_NVIDIA_Techs

UNITY HAIRWORKS PORT :

https://github.com/unity3d-jp/NVIDIAHairWorksIntegration

TUTORIAL VIDEO :

https://www.youtube.com/watch?v=mnVRQpPsRVE
