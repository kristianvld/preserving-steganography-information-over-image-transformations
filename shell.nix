# Packages are locked to the commit 9334a29720c76dcfdbc54ec9e8703473aa1729d8
# to make sure this repository is reproducable and that all packagers are
# available and at the same versions as the ones used in this repository.
{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/9334a29720c76dcfdbc54ec9e8703473aa1729d8.tar.gz") {} }:
  pkgs.mkShell {
    buildInputs = with pkgs; [
      zbar
      zxing
      adoptopenjdk-jre-bin
    ];
    nativeBuildInputs = with pkgs; [ 
      python39Packages.numpy
      python39Packages.scipy
      python39Packages.opencv3
      steghide
      imagemagick
      pipenv
    ];
}
