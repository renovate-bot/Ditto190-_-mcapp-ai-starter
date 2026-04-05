{ lib, rustPlatform, fetchFromGitHub, pkg-config, openssl, zlib }:

rustPlatform.buildRustPackage rec {
  pname = "fff-mcp";
  version = "0.5.1";

  src = fetchFromGitHub {
    owner = "dmtrKovalenko";
    repo = "fff.nvim";
    rev = "v0.5.1";
    sha256 = "a137effce2bb40da142d5a0e996116e6fe3b25a93b235cbb9b4c59d1d63387b8";
  };

  subdir = "crates/fff-mcp";

  cargoSha256 = lib.fakeSha256;

  nativeBuildInputs = [ pkg-config ];
  buildInputs = [ openssl zlib ];

  cargoFeatures = [ "zlob" ];

  meta = with lib; {
    description = "MCP server for FFF file finder";
    license = licenses.mit;
    homepage = "https://github.com/dmtrKovalenko/fff.nvim";
  };
}
