{ pkgs }: {
  deps = [
    pkgs.python310Full
    pkgs.python310Packages.pip
    pkgs.python310Packages.opencv4
    pkgs.python310Packages.mediapipe
    pkgs.python310Packages.face-recognition
    pkgs.python310Packages.dlib
    pkgs.tkinter
  ];
}
