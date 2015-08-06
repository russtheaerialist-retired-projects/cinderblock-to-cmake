# Cinderblock.xml to cmake

Allows for easy use of cinderblocks when using cmake+ninja rather than Tinderbox.

### problem

While most people use Tinderbox to work with cinder, I don't like xcode, and I'd rather build using Ninja.  I have a cinder app template that uses cmake+ninja to build
cinder applications, and it works great, but it requires a large amount of tweaking of the cmake files: adding in source and headers, targetting the correct osx, linking
the libraries.  But these are all very similar changes, and all the necessary information is already in the cinderblocks.xml, so why not automate it.

## Install

This is written for python3, though I can't imagine it would break under python2, but it hasn't been tested.

1. Clone the repository
1. cd into cinderblock-to-cmake
1. python3 setup.py install

## Usage

From the root of your cmake project:

1. run `b2cm` with the relative path of the directory of your block as the argument.
1. Redirect this output into a .cmake file.
1. Add `include(name-of-cmake-file)` to your main CMakeLists.txt.

See my [cinder-cmake-template](https://github.com/RussTheAerialist/cinder-cmake-template) repo for an example of how to use it.

## Current State

I've only tested the script with OSX, and only on the Cinder-Kinect block.  I'm very much open to contributions.  Open a pull request, be sure to include your name in the
CONTRIBUTERS.md file
