# EAF Map
<p align="center">
  <img width="800" src="./screenshot.png">
</p>

This repository provides the EAF OpenStreetMap application for the [Emacs Application Framework](https://github.com/emacs-eaf/emacs-application-framework).

### Load application

[Install EAF](https://github.com/emacs-eaf/emacs-application-framework#install) first, then add below code in your emacs config:

```Elisp
(add-to-list 'load-path "~/.emacs.d/site-lisp/emacs-application-framework/")
(require 'eaf)
(require 'eaf-map)
```

### The keybinding of EAF Vue demo.

| Key   | Event   |
| :---- | :------ |
| `<f12>` | open_devtools |
| `a` | add_place |
| `d` | delete_place |
| `x` | sort_places |
| `o` | open_map |
| `s` | save_map |
| `t` | js_toggle_distance_tip |

