{ pkgs }: {
    deps = [
        pkgs.python312
        pkgs.python312Packages.pip
        pkgs.nodejs
        pkgs.chromium
        pkgs.chromedriver
        pkgs.geckodriver
    ];
    env = {
        PYTHONBIN = "${pkgs.python312}/bin/python3.12";
        LANG = "en_US.UTF-8";
        PLAYWRIGHT_BROWSERS_PATH = "${pkgs.chromium}";
    };
} 