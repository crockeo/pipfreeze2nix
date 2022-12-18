# NOTE: this isn't actually generated from the requirements.txt as it exists right now.
# this was hand-modified to generate a valid set of dependencies.
# but this is representative of how the requirements.txt will look soon :)
{ python, nixpkgs }:
let
  certifi = (python.pkgs.buildPythonPackage rec {
    pname = "certifi";
    version = "2022.12.7";
    format = "wheel";

    doCheck = false;

    src = builtins.fetchurl {
      url = "https://files.pythonhosted.org/packages/71/4c/3db2b8021bd6f2f0ceb0e088d6b2d49147671f25832fb17970e9b583d742/certifi-2022.12.7-py3-none-any.whl";
      sha256 = "4ad3232f5e926d6718ec31cfc1fcadfde020920e278684144551c91769c7bc18";
    };
  });

  charset-normalizer = (python.pkgs.buildPythonPackage rec {
    pname = "charset-normalizer";
    version = "2.1.1";
    format = "wheel";

    doCheck = false;

    src = builtins.fetchurl {
      url = "https://files.pythonhosted.org/packages/db/51/a507c856293ab05cdc1db77ff4bc1268ddd39f29e7dc4919aa497f0adbec/charset_normalizer-2.1.1-py3-none-any.whl";
      sha256 = "83e9a75d1911279afd89352c68b45348559d1fc0506b054b346651b5e7fee29f";
    };
  });

  idna = (python.pkgs.buildPythonPackage rec {
    pname = "idna";
    version = "3.4";
    format = "wheel";

    doCheck = false;

    src = builtins.fetchurl {
      url = "https://files.pythonhosted.org/packages/fc/34/3030de6f1370931b9dbb4dad48f6ab1015ab1d32447850b9fc94e60097be/idna-3.4-py3-none-any.whl";
      sha256 = "90b77e79eaa3eba6de819a0c442c0b4ceefc341a7a2ab77d7562bf49f425c5c2";
    };
  });

  urllib3 = (python.pkgs.buildPythonPackage rec {
    pname = "urllib3";
    version = "1.26.13";
    format = "wheel";

    doCheck = false;

    src = builtins.fetchurl {
      url = "https://files.pythonhosted.org/packages/65/0c/cc6644eaa594585e5875f46f3c83ee8762b647b51fc5b0fb253a242df2dc/urllib3-1.26.13-py2.py3-none-any.whl";
      sha256 = "47cc05d99aaa09c9e72ed5809b60e7ba354e64b59c9c173ac3018642d8bb41fc";
    };
  });

  requests = (python.pkgs.buildPythonPackage rec {
    pname = "requests";
    version = "2.28.1";
    format = "wheel";

    doCheck = false;

    propagatedBuildInputs = [
      certifi
      charset-normalizer
      idna
      urllib3
    ];

    src = builtins.fetchurl {
      url = "https://files.pythonhosted.org/packages/ca/91/6d9b8ccacd0412c08820f72cebaa4f0c0441b5cda699c90f618b6f8a1b42/requests-2.28.1-py3-none-any.whl";
      sha256 = "8fefa2a1a1365bf5520aac41836fbee479da67864514bdb821f31ce07ce65349";
    };
  });

  packaging = (python.pkgs.buildPythonPackage rec {
    pname = "packaging";
    version = "22.0";
    format = "wheel";

    doCheck = false;

    src = builtins.fetchurl {
      url = "https://files.pythonhosted.org/packages/8f/7b/42582927d281d7cb035609cd3a543ffac89b74f3f4ee8e1c50914bcb57eb/packaging-22.0-py3-none-any.whl";
      sha256 = "957e2148ba0e1a3b282772e791ef1d8083648bc131c8ab0c1feba110ce1146c3";
    };
  });
in
[
  certifi
  charset-normalizer
  idna
  packaging
  requests
  urllib3
]
