{ python, nixpkgs }:
[
    (python.pkgs.buildPythonPackage rec {
    pname = "certifi";
    version = "2022.12.7";

    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "35824b4c3a97115964b408844d64aa14db1cc518f6562e8d7261699d1350a9e3";
    };
  })
  (python.pkgs.buildPythonPackage rec {
    pname = "charset-normalizer";
    version = "2.1.1";

    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "5a3d016c7c547f69d6f81fb0db9449ce888b418b5b9952cc5e6e66843e9dd845";
    };
  })
  (python.pkgs.buildPythonPackage rec {
    pname = "idna";
    version = "3.4";

    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "814f528e8dead7d329833b91c5faa87d60bf71824cd12a7530b5526063d02cb4";
    };
  })
  (python.pkgs.buildPythonPackage rec {
    pname = "packaging";
    version = "22.0";

    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "2198ec20bd4c017b8f9717e00f0c8714076fc2fd93816750ab48e2c41de2cfd3";
    };
  })
  (python.pkgs.buildPythonPackage rec {
    pname = "requests";
    version = "2.28.1";

    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "7c5599b102feddaa661c826c56ab4fee28bfd17f5abca1ebbe3e7f19d7c97983";
    };
  })
  (python.pkgs.buildPythonPackage rec {
    pname = "urllib3";
    version = "1.26.13";

    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "c083dd0dce68dbfbe1129d5271cb90f9447dea7d52097c6e0126120c521ddea8";
    };
  })
]
