# Airport ✈️

Airport is a tool for managing portage, Gentoo's package manager. It is made
with USE flags in mind, meaning that you can exclude the features that you
don't need (such as a Qt GUI interface).

## Installation

You don't need to make a custom ebuild for airport; check out my [personal
overlay](https://github.com/BraveeSnow/snowverlay), which already includes it!

```
# eselect repository add snowverlay git https://github.com/BraveeSnow/snowverlay.git
# emaint sync -r snowverlay
# emerge airport
```

## Requirements

- Python 3.10+
- PySide6
