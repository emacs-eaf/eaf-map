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

### Gaode Map API
If you have [Gaode Map API Key](https://lbs.amap.com), put fill key in ```~/.emacs.d/eaf/map/gaode_api_key.txt```, then eaf-map will use Gaode API instead OpenStreetMap API, API's response is much faster in China.

### The keybinding of EAF Map.

| Key   | Event   |
| :---- | :------ |
| `<f12>` | open_devtools |
| `a` | add_place |
| `d` | delete_place |
| `x` | sort_places |
| `o` | open_map |
| `s` | save_map |
| `r` | reload_map |
| `t` | js_toggle_distance_tip |
| `-` | js_zoom_out |
| `=` | js_zoom_in |
| `j` | js_move_up |
| `k` | js_move_down |
| `h` | js_move_left |
| `l` | js_move_right |

