{ python, nixpkgs }:
let
  attrs = (python.pkgs.buildPythonPackage rec {
    pname = "attrs";
    version = "22.1.0";
    format = "wheel";

    doCheck = false;

    propagatedBuildInputs = [

    ];

    src = builtins.fetchurl {
      url = "https://files.pythonhosted.org/packages/f2/bc/d817287d1aa01878af07c19505fafd1165cd6a119e9d0821ca1d1c20312d/attrs-22.1.0-py2.py3-none-any.whl";
      sha256 = "86efa402f67bf2df34f51a335487cf46b1ec130d02b8d39fd248abfd30da551c";
    };
  });
  certifi = (python.pkgs.buildPythonPackage rec {
    pname = "certifi";
    version = "2022.12.7";
    format = "wheel";

    doCheck = false;

    propagatedBuildInputs = [

    ];

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

    propagatedBuildInputs = [

    ];

    src = builtins.fetchurl {
      url = "https://files.pythonhosted.org/packages/db/51/a507c856293ab05cdc1db77ff4bc1268ddd39f29e7dc4919aa497f0adbec/charset_normalizer-2.1.1-py3-none-any.whl";
      sha256 = "83e9a75d1911279afd89352c68b45348559d1fc0506b054b346651b5e7fee29f";
    };
  });
  exceptiongroup = (python.pkgs.buildPythonPackage rec {
    pname = "exceptiongroup";
    version = "1.0.4";
    format = "wheel";

    doCheck = false;

    propagatedBuildInputs = [

    ];

    src = builtins.fetchurl {
      url = "https://files.pythonhosted.org/packages/ce/2e/9a327cc0d2d674ee2d570ee30119755af772094edba86d721dda94404d1a/exceptiongroup-1.0.4-py3-none-any.whl";
      sha256 = "542adf9dea4055530d6e1279602fa5cb11dab2395fa650b8674eaec35fc4a828";
    };
  });
  idna = (python.pkgs.buildPythonPackage rec {
    pname = "idna";
    version = "3.4";
    format = "wheel";

    doCheck = false;

    propagatedBuildInputs = [

    ];

    src = builtins.fetchurl {
      url = "https://files.pythonhosted.org/packages/fc/34/3030de6f1370931b9dbb4dad48f6ab1015ab1d32447850b9fc94e60097be/idna-3.4-py3-none-any.whl";
      sha256 = "90b77e79eaa3eba6de819a0c442c0b4ceefc341a7a2ab77d7562bf49f425c5c2";
    };
  });
  iniconfig = (python.pkgs.buildPythonPackage rec {
    pname = "iniconfig";
    version = "1.1.1";
    format = "wheel";

    doCheck = false;

    propagatedBuildInputs = [

    ];

    src = builtins.fetchurl {
      url = "https://files.pythonhosted.org/packages/9b/dd/b3c12c6d707058fa947864b67f0c4e0c39ef8610988d7baea9578f3c48f3/iniconfig-1.1.1-py2.py3-none-any.whl";
      sha256 = "011e24c64b7f47f6ebd835bb12a743f2fbe9a26d4cecaa7f53bc4f35ee9da8b3";
    };
  });
  packaging = (python.pkgs.buildPythonPackage rec {
    pname = "packaging";
    version = "22.0";
    format = "wheel";

    doCheck = false;

    propagatedBuildInputs = [

    ];

    src = builtins.fetchurl {
      url = "https://files.pythonhosted.org/packages/8f/7b/42582927d281d7cb035609cd3a543ffac89b74f3f4ee8e1c50914bcb57eb/packaging-22.0-py3-none-any.whl";
      sha256 = "957e2148ba0e1a3b282772e791ef1d8083648bc131c8ab0c1feba110ce1146c3";
    };
  });
  pluggy = (python.pkgs.buildPythonPackage rec {
    pname = "pluggy";
    version = "1.0.0";
    format = "wheel";

    doCheck = false;

    propagatedBuildInputs = [

    ];

    src = builtins.fetchurl {
      url = "https://files.pythonhosted.org/packages/9e/01/f38e2ff29715251cf25532b9082a1589ab7e4f571ced434f98d0139336dc/pluggy-1.0.0-py2.py3-none-any.whl";
      sha256 = "74134bbf457f031a36d68416e1509f34bd5ccc019f0bcc952c7b909d06b37bd3";
    };
  });
  tomli = (python.pkgs.buildPythonPackage rec {
    pname = "tomli";
    version = "2.0.1";
    format = "wheel";

    doCheck = false;

    propagatedBuildInputs = [

    ];

    src = builtins.fetchurl {
      url = "https://files.pythonhosted.org/packages/97/75/10a9ebee3fd790d20926a90a2547f0bf78f371b2f13aa822c759680ca7b9/tomli-2.0.1-py3-none-any.whl";
      sha256 = "939de3e7a6161af0c887ef91b7d41a53e7c5a1ca976325f429cb46ea9bc30ecc";
    };
  });
  urllib3 = (python.pkgs.buildPythonPackage rec {
    pname = "urllib3";
    version = "1.26.13";
    format = "wheel";

    doCheck = false;

    propagatedBuildInputs = [

    ];

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
  pytest = (python.pkgs.buildPythonPackage rec {
    pname = "pytest";
    version = "7.2.0";
    format = "wheel";

    doCheck = false;

    propagatedBuildInputs = [
      attrs
  exceptiongroup
  iniconfig
  packaging
  pluggy
  tomli
    ];

    src = builtins.fetchurl {
      url = "https://files.pythonhosted.org/packages/67/68/a5eb36c3a8540594b6035e6cdae40c1ef1b6a2bfacbecc3d1a544583c078/pytest-7.2.0-py3-none-any.whl";
      sha256 = "892f933d339f068883b6fd5a459f03d85bfcb355e4981e146d2c7616c21fef71";
    };
  });
in
[
packaging
requests
pytest]
