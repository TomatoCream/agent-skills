---
name: df-treefmt-nix
description: Use when setting up treefmt-nix in a Nix flake, configuring `nix fmt` or `nix flake check`, integrating treefmt-nix with flake-parts, enabling or tuning formatters (nixfmt, prettier, black, rustfmt, terraform, gofmt, etc.), setting formatter priorities, writing custom formatter definitions, or using evalModule/mkWrapper/mkConfigFile APIs.
---

### Set up treefmt-nix with Nix Flakes

Source: https://github.com/numtide/treefmt-nix/blob/main/README.md

This `flake.nix` configures `treefmt-nix` for use with Nix flakes. It defines inputs for `treefmt-nix` and Nix systems, and exposes a `formatter` output for `nix fmt` and a `checks` output for `nix flake check`.

```nix
# flake.nix
{
  inputs.treefmt-nix.url = "github:numtide/treefmt-nix";
  inputs.systems.url = "github:nix-systems/default";

  outputs = { self, nixpkgs, systems, treefmt-nix }:
    let
      # Small tool to iterate over each systems
      eachSystem = f: nixpkgs.lib.genAttrs (import systems) (system: f nixpkgs.legacyPackages.${system});

      # Eval the treefmt modules from ./treefmt.nix
      treefmtEval = eachSystem (pkgs: treefmt-nix.lib.evalModule pkgs ./treefmt.nix);
    in
    {
      # for `nix fmt`
      formatter = eachSystem (pkgs: treefmtEval.${pkgs.system}.config.build.wrapper);
      # for `nix flake check`
      checks = eachSystem (pkgs: {
        formatting = treefmtEval.${pkgs.system}.config.build.check self;
      });
    };
}
```

--------------------------------

### Integrate treefmt-nix with Nix Classic (niv)

Source: https://github.com/numtide/treefmt-nix/blob/main/README.md

This snippet shows how to add treefmt-nix to a Nix project using the `niv` tool for dependency management. It fetches the latest version from GitHub and makes it available for use in your Nix expressions.

```bash
$ niv add numtide/treefmt-nix
```

--------------------------------

### Flakes Integration - nix fmt integration

Source: https://context7.com/numtide/treefmt-nix/llms.txt

Integrates treefmt-nix with Nix flakes to enable the standard `nix fmt` command and `nix flake check` for CI validation.

```nix
# flake.nix
{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    treefmt-nix.url = "github:numtide/treefmt-nix";
    systems.url = "github:nix-systems/default";
  };

  outputs = { self, nixpkgs, systems, treefmt-nix }:
    let
      eachSystem = f: nixpkgs.lib.genAttrs (import systems) (system: f nixpkgs.legacyPackages.${system});
      treefmtEval = eachSystem (pkgs: treefmt-nix.lib.evalModule pkgs ./treefmt.nix);
    in
    {
      # Enable: nix fmt
      formatter = eachSystem (pkgs: treefmtEval.${pkgs.system}.config.build.wrapper);

      # Enable: nix flake check
      checks = eachSystem (pkgs: {
        formatting = treefmtEval.${pkgs.system}.config.build.check self;
      });

      # Development shell with formatters
      devShells = eachSystem (pkgs: {
        default = treefmtEval.${pkgs.system}.config.build.devShell;
      });
    };
}
```

--------------------------------

### Update README with mdsh

Source: https://github.com/numtide/treefmt-nix/blob/main/README.md

These shell and Nix commands illustrate how to automatically update the README.md file, likely to reflect supported programs or configurations, using the 'mdsh' tool.

```bash
mdsh -i README.md -o README.md

```

```nix
nix run github:zimbatm/mdsh -- -i README.md -o README.md

```

--------------------------------

### Flake-parts Integration for treefmt-nix

Source: https://context7.com/numtide/treefmt-nix/llms.txt

This example demonstrates how to integrate treefmt-nix as a module within a flake-parts setup. It allows configuring various formatters, including Prettier with custom settings, and defining global excludes.

```nix
# flake.nix
{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    treefmt-nix.url = "github:numtide/treefmt-nix";
  };

  outputs = inputs @ { flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [ "x86_64-linux" "aarch64-linux" "aarch64-darwin" "x86_64-darwin" ];

      imports = [
        inputs.treefmt-nix.flakeModule
      ];

      perSystem = { config, pkgs, ... }: {
        # Configure treefmt in perSystem
        treefmt = {
          projectRootFile = "flake.nix";

          programs.prettier.enable = true;
          programs.prettier.settings = {
            tabWidth = 2;
            singleQuote = true;
            trailingComma = "es5";
          };

          programs.eslint.enable = true;
          programs.rustfmt.enable = true;
          programs.black.enable = true;

          settings.global.excludes = [ "dist/*" "build/*" ];
        };

        # treefmt-nix automatically sets:
        # - formatter.${system} = treefmt wrapper
        # - checks.${system}.treefmt = formatting check
      };
    };
}

# Access with:
# nix fmt
# nix flake check
```

--------------------------------

### Evaluate treefmt-nix Configuration with evalModule

Source: https://context7.com/numtide/treefmt-nix/llms.txt

The `evalModule` function evaluates a treefmt-nix configuration. It takes the nixpkgs set as an argument and returns a structure containing validated configuration and build outputs, such as a wrapped treefmt binary, generated configuration file, and a development shell. Dependencies include nixpkgs and treefmt-nix. Inputs are Nix expressions defining formatter settings.

```nix
let
  treefmt-nix = import (builtins.fetchGit {
    url = "https://github.com/numtide/treefmt-nix";
    ref = "main";
  });

  nixpkgs = import <nixpkgs> { };

  # Evaluate the configuration
  evaluated = treefmt-nix.evalModule nixpkgs {
    projectRootFile = "flake.nix";
    programs.black.enable = true;
    programs.prettier.enable = true;
    programs.rustfmt.enable = true;
    settings.formatter.prettier.excludes = [ "*.min.js" ];
  };
in
# Access build outputs
{
  wrapper = evaluated.config.build.wrapper;      # The wrapped treefmt binary
  configFile = evaluated.config.build.configFile; # Generated treefmt.toml
  devShell = evaluated.config.build.devShell;    # Development shell with formatters
}
```

--------------------------------

### Enable Multiple Formatters with treefmt-nix (Nix)

Source: https://github.com/numtide/treefmt-nix/blob/main/README.md

This snippet illustrates how to enable multiple formatters, specifically Terraform and gofmt, using Nix syntax within treefmt-nix. This allows for the concurrent use of various code formatters in a project.

```nix
programs.terraform.enable = true;
programs.gofmt.enable = true;
```

--------------------------------

### Basic treefmt.nix Configuration

Source: https://context7.com/numtide/treefmt-nix/llms.txt

This snippet shows a basic configuration for treefmt-nix, enabling several common Nix-related formatters. It defines the project root file and enables nixfmt, deadnix, and statix.

```nix
{ pkgs, ... }:
{
  projectRootFile = "flake.nix";
  programs.nixfmt.enable = true;
  programs.deadnix.enable = true;
  programs.statix.enable = true;
}
```

--------------------------------

### Program-Specific Settings in treefmt-nix

Source: https://context7.com/numtide/treefmt-nix/llms.txt

This configuration illustrates how to set program-specific options and overrides for formatters. It includes detailed settings for Prettier, specifies a particular Python version for Black, configures Terraform, and manages formatter priorities and global excludes.

```nix
{ pkgs, ... }:
{
  projectRootFile = "flake.nix";

  # Prettier with detailed configuration
  programs.prettier.enable = true;
  programs.prettier.package = pkgs.nodePackages.prettier;
  programs.prettier.includes = [ "*.js" "*.jsx" "*.ts" "*.tsx" "*.css" "*.md" ];
  programs.prettier.excludes = [ "dist/*" "coverage/*" ];
  programs.prettier.settings = {
    printWidth = 100;
    tabWidth = 2;
    useTabs = false;
    semi = true;
    singleQuote = true;
    trailingComma = "es5";
    bracketSpacing = true;
    arrowParens = "always";
  };

  # Black with specific Python version
  programs.black.enable = true;
  programs.black.package = pkgs.python311Packages.black;

  # Terraform with specific version
  programs.terraform.enable = true;
  programs.terraform.package = pkgs.terraform_1;
  programs.terraform.excludes = [ "*.tfstate" ".terraform/*" ];

  # Override formatter priority (lower runs first)
  programs.goimports.enable = true;
  programs.goimports.priority = 1;
  programs.gofmt.enable = true;
  programs.gofmt.priority = 2;

  # Global excludes applied to all formatters
  settings.global.excludes = [
    "*.lock"
    "node_modules/*"
    "vendor/*"
    ".git/*"
  ];

  # Control unmatched file logging
  settings.global.on-unmatched = "info";
}
```

--------------------------------

### Configure treefmt-nix formatters and settings (Flakes)

Source: https://github.com/numtide/treefmt-nix/blob/main/README.md

This Nix file defines the configuration for `treefmt-nix` when using flakes. It sets the `projectRootFile` to `flake.nix`, enables and configures the Terraform formatter, including package overrides and exclusion rules.

```nix
# treefmt.nix
{ pkgs, ... }:
{
  # Used to find the project root
  projectRootFile = "flake.nix";
  # Enable the terraform formatter
  programs.terraform.enable = true;
  # Override the default package
  programs.terraform.package = pkgs.terraform_1;
  # Override the default settings generated by the above option
  settings.formatter.terraform.excludes = [ "hello.tf" ];
}
```

--------------------------------

### Accessing treefmt-nix Build Outputs in Nix

Source: https://context7.com/numtide/treefmt-nix/llms.txt

This Nix code snippet demonstrates how to evaluate the treefmt-nix module and access its various build outputs, such as a wrapped binary, configuration file, development shell, and formatter packages.

```nix
let
  nixpkgs = import <nixpkgs> { };
  treefmt-nix = import ./treefmt-nix;

  eval = treefmt-nix.evalModule nixpkgs {
    projectRootFile = "flake.nix";
    programs.black.enable = true;
    programs.rustfmt.enable = true;
    programs.prettier.enable = true;
  };

  config = eval.config;
in
{
  # Wrapped treefmt binary ready to use
  wrapper = config.build.wrapper;
  # Usage: ${wrapper}/bin/treefmt

  # Generated treefmt.toml config file
  configFile = config.build.configFile;
  # Usage: treefmt --config-file ${configFile}

  # Development shell with all formatters
  devShell = config.build.devShell;
  # Usage: nix-shell -A devShell

  # Attrset of enabled formatter packages
  programs = config.build.programs;
  # Example: programs.black, programs.prettier

  # Function to create CI check
  check = config.build.check;
  # Usage: check ./path/to/project
  # Returns derivation that fails if code is not formatted
}

```

--------------------------------

### Configure Custom JSON Formatter with yq-go

Source: https://github.com/numtide/treefmt-nix/blob/main/README.md

This Nix code snippet demonstrates how to configure a custom formatter for JSON files using 'yq-go'. It defines the command, options, and file inclusions for the formatter.

```nix
settings.formatter = {
  "yq-json" = {
    command = "${pkgs.bash}/bin/bash";
    options = [
      "-euc"
      ''
        for file in "$@"; do
          ${lib.getExe yq-go} -i --output-format=json $file
        done
      ''
      "--" # bash swallows the second argument when using -c
    ];
    includes = [ "*.json" ];
  };
};

```

--------------------------------

### Setting Formatter Priority in Nix with treefmt-nix

Source: https://context7.com/numtide/treefmt-nix/llms.txt

This Nix snippet illustrates how to control the execution order of formatters using the 'priority' setting in treefmt-nix. It shows explicit priority settings for Go and Python formatters, with a default priority for others.

```nix
{ pkgs, ... }:
{
  projectRootFile = "flake.nix";

  # Run goimports first to organize imports
  programs.goimports.enable = true;
  programs.goimports.priority = 1;

  # Then run gofumpt for additional formatting
  programs.gofumpt.enable = true;
  programs.gofumpt.priority = 2;

  # Then run golangci-lint to fix linting issues
  programs.golangci-lint.enable = true;
  programs.golangci-lint.priority = 3;
  settings.formatter.golangci-lint.options = [ "--fix" ];

  # For Python: run isort first, then black
  programs.isort.enable = true;
  programs.isort.priority = 10;

  programs.black.enable = true;
  programs.black.priority = 11;

  # Default priority (no priority set) runs after all explicit priorities
  programs.prettier.enable = true;
}

```

--------------------------------

### Nix Module Configuration for treefmt-nix

Source: https://context7.com/numtide/treefmt-nix/llms.txt

This snippet shows how to integrate treefmt-nix into a Nix module, enabling formatters like nixfmt and black. It defines options for formatting configuration and sets default formatting behavior.

```nix
{ lib, pkgs, ... }:
let
  treefmt-nix = import ./path/to/treefmt-nix;

  treefmtSubmodule = treefmt-nix.submoduleWith lib {
    modules = [
      # Additional custom modules specific to your system
      ({ config, ... }: {
        config.programs.custom-formatter.enable = true;
      })
    ];
    specialArgs = {
      # Additional arguments passed to all submodules
      myCustomArg = "value";
    };
  };
in
{
  options = {
    formatting = lib.mkOption {
      type = treefmtSubmodule;
      description = "Formatting configuration";
      default = { };
    };
  };

  config = {
    formatting = {
      pkgs = pkgs;
      projectRootFile = "flake.nix";
      programs.nixfmt.enable = true;
      programs.black.enable = true;
    };
  };
}

```

--------------------------------

### mkWrapper - Create wrapped treefmt executable

Source: https://context7.com/numtide/treefmt-nix/llms.txt

Creates a treefmt binary wrapped with the specified configuration, ready to format files without requiring a separate `treefmt.toml` file.

```nix
# standalone-formatter.nix
{
  system ? builtins.currentSystem
}:
let
  nixpkgsSrc = builtins.fetchTarball
    "https://github.com/NixOS/nixpkgs/archive/refs/heads/nixos-unstable.tar.gz";
  treefmt-nixSrc = builtins.fetchTarball
    "https://github.com/numtide/treefmt-nix/archive/refs/heads/master.tar.gz";

  nixpkgs = import nixpkgsSrc { inherit system; };
  treefmt-nix = import treefmt-nixSrc;
in
treefmt-nix.mkWrapper nixpkgs {
  projectRootFile = ".git/config";

  # Enable multiple formatters
  programs.terraform.enable = true;
  programs.terraform.package = nixpkgs.terraform_1;
  programs.black.enable = true;
  programs.prettier.enable = true;
  programs.rustfmt.enable = true;

  # Override formatter settings
  settings.formatter.terraform.excludes = [ "terraform.tfstate" "*.tfstate" ];
  settings.formatter.prettier.options = [ "--tab-width" "4" ];
  settings.global.excludes = [ "node_modules/*" "vendor/*" ];
}

# Build with: nix-build standalone-formatter.nix
# Run with: ./result/bin/treefmt
```

--------------------------------

### mkConfigFile - Generate treefmt.toml configuration

Source: https://context7.com/numtide/treefmt-nix/llms.txt

Generates a `treefmt.toml` configuration file from Nix expressions without creating a wrapper binary.

```nix
let
  nixpkgs = import <nixpkgs> { };
  treefmt-nix = import ./path/to/treefmt-nix;

  configFile = treefmt-nix.mkConfigFile nixpkgs {
    projectRootFile = "flake.nix";
    programs.gofmt.enable = true;
    programs.goimports.enable = true;
    programs.golangci-lint.enable = true;

    settings.formatter.golangci-lint.options = [ "--fix" ];
    settings.formatter.golangci-lint.includes = [ "*.go" ];
    settings.global.excludes = [ "vendor/*" "*_test.go" ];
  };
in
# The configFile is a path to the generated treefmt.toml in /nix/store
# Use it directly: treefmt --config-file ${configFile}
configFile
```

--------------------------------

### Configure treefmt-nix for Terraform (Nix Classic)

Source: https://github.com/numtide/treefmt-nix/blob/main/README.md

This Nix expression configures `treefmt-nix` to format Terraform files. It specifies the project root, enables the Terraform formatter, overrides the default package to `terraform_1`, and sets exclusions for specific files.

```nix
# myfile.nix
{
  system ? builtins.currentSystem
}:
let
  nixpkgsSrc = builtins.fetchTarball "https://github.com/NixOS/nixpkgs/archive/refs/heads/nixos-unstable.tar.gz";
  treefmt-nixSrc = builtins.fetchTarball "https://github.com/numtide/treefmt-nix/archive/refs/heads/master.tar.gz";
  nixpkgs = import nixpkgsSrc { inherit system; };
  treefmt-nix = import treefmt-nixSrc;
in
treefmt-nix.mkWrapper nixpkgs {
  # Used to find the project root
  projectRootFile = ".git/config";
  # Enable the terraform formatter
  programs.terraform.enable = true;
  # Override the default package
  programs.terraform.package = nixpkgs.terraform_1;
  # Override the default settings generated by the above option
  settings.formatter.terraform.excludes = [ "hello.tf" ];
}
```

--------------------------------

### Creating Custom Formatter Modules with mkFormatterModule in Nix

Source: https://context7.com/numtide/treefmt-nix/llms.txt

This Nix code example demonstrates the use of the `mkFormatterModule` helper function in treefmt-nix to define custom formatter modules. It shows configurations for basic inclusion, custom package names, and default arguments with include/exclude patterns.

```nix
# custom-formatters.nix
{ mkFormatterModule, ... }:
{
  imports = [
    # Simple formatter with just includes
    (mkFormatterModule {
      name = "my-formatter";
      includes = [ "*.myext" ];
    })

    # Formatter with custom package name
    (mkFormatterModule {
      name = "my-formatter";
      package = "my-formatter-pkg";
      mainProgram = "my-fmt";
      includes = [ "*.txt" ];
    })

    # Formatter with default arguments
    (mkFormatterModule {
      name = "my-formatter";
      args = [ "--fix" "--write" ];
      includes = [ "*.data" ];
      excludes = [ "*.generated.data" ];
    })
  ];

  # The module automatically creates:
  # - programs.my-formatter.enable option
  # - programs.my-formatter.package option
  # - programs.my-formatter.includes option
  # - programs.my-formatter.excludes option
  # - programs.my-formatter.priority option
}

```

--------------------------------

### Custom Formatter Configuration in treefmt-nix

Source: https://context7.com/numtide/treefmt-nix/llms.txt

This example shows how to define custom formatters for file types not covered by the built-in options. It includes configurations for `yq-go` to format JSON, `shfmt` for shell scripts, and `pylint` for Python code.

```nix
{ pkgs, lib, ... }:
{
  projectRootFile = "flake.nix";

  # Use built-in formatters
  programs.prettier.enable = true;

  # Define custom formatter using yq-go for JSON formatting
  settings.formatter.yq-json = {
    command = "${pkgs.bash}/bin/bash";
    options = [
      "-euc"
      ''
        for file in "$@"; do
          ${lib.getExe pkgs.yq-go} -i --output-format=json "$file"
        done
      ''
      "--"
    ];
    includes = [ "*.json" ];
    excludes = [ "package-lock.json" ];
  };

  # Custom shell formatter with specific options
  settings.formatter.custom-shfmt = {
    command = "${pkgs.shfmt}/bin/shfmt";
    options = [ "-i" "2" "-sr" "-w" ];
    includes = [ "*.sh" "*.bash" ];
    excludes = [ "vendor/*" ];
  };

  # Custom Python linter in addition to formatter
  settings.formatter.pylint = {
    command = "${pkgs.python3Packages.pylint}/bin/pylint";
    options = [ "--output-format=text" "--score=no" ];
    includes = [ "*.py" ];
    excludes = [ "tests/*" "__pycache__/*" ];
  };
}
```
